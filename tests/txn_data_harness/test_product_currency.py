"""Currency selection must stay consistent from config through resume/payloads."""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from scripts.txn_data_harness import config, discovery, runner, cli, lifecycle
from scripts.txn_data_harness.models import LineItem


def pbe(currency='USD', model='Annual', suffix=''):
    return {'Id': f'pbe-{currency}-{model}{suffix}', 'Product2Id': 'product',
            'CurrencyIsoCode': currency, 'UnitPrice': 450,
            'Product2': {'Name': 'Widget', 'StockKeepingUnit': 'SKU'},
            'ProductSellingModel': {'Name': model, 'SellingModelType': 'OneTime'}}


def test_currency_and_model_both_required(fake_client):
    fake_client.query_responses = [[pbe(c, m) for c in ['USD', 'EUR'] for m in ['Annual', 'Monthly']]]
    product = discovery.resolve_product(fake_client, 'SKU', 'Monthly', 'EUR')
    assert product.pricebook_entry_id == 'pbe-EUR-Monthly'
    assert product.currency_iso_code == 'EUR'


def test_currency_does_not_hide_model_ambiguity(fake_client):
    fake_client.query_responses = [[pbe('EUR', m) for m in ['Annual', 'Monthly']]]
    with pytest.raises(discovery.DiscoveryError, match='selling_model'):
        discovery.resolve_product(fake_client, 'SKU', currency='EUR')


def test_missing_currency_reports_available(fake_client):
    fake_client.query_responses = [[pbe('USD')]]
    with pytest.raises(discovery.DiscoveryError, match="currency 'EUR'.*USD"):
        discovery.resolve_product(fake_client, 'SKU', currency='EUR')


def test_same_currency_duplicate_pbes_still_fail(fake_client):
    fake_client.query_responses = [[pbe(), pbe(suffix='2')]]
    with pytest.raises(discovery.DiscoveryError, match='expected exactly one'):
        discovery.resolve_product(fake_client, 'SKU', 'Annual', 'USD')


def test_sku_query_has_no_25_row_truncation(fake_client):
    fake_client.query_responses = [[pbe(str(i)) for i in range(30)] + [pbe('EUR')]]
    assert discovery.resolve_product(fake_client, 'SKU', currency='EUR').currency_iso_code == 'EUR'
    assert 'LIMIT' not in fake_client.queries[0]


def test_single_currency_retry_omits_only_currency_field(fake_client):
    calls = []
    def query(sql):
        calls.append(sql)
        if 'CurrencyIsoCode' in sql:
            raise RuntimeError('INVALID_FIELD: CurrencyIsoCode')
        row = pbe(); row.pop('CurrencyIsoCode')
        return [row]
    fake_client.query = query
    assert discovery.resolve_product(fake_client, 'SKU').currency_iso_code is None
    assert len(calls) == 2
    assert 'ProductSellingModel.Name' in calls[1]


@pytest.mark.parametrize('error', ['INVALID_FIELD: Product2.Name', 'INVALID_SESSION_ID', 'timeout'])
def test_currency_probe_does_not_hide_other_errors(fake_client, error):
    def query(sql):
        raise RuntimeError(error)
    fake_client.query = query
    with pytest.raises(RuntimeError, match=error):
        discovery.resolve_product(fake_client, 'SKU')


@pytest.mark.parametrize('raw', [123, True, '', 'US', 'EURO', ['USD']])
def test_bad_currency_config_rejected(raw):
    with pytest.raises(config.ConfigError, match='currency'):
        config._coerce_sales_transaction_spec({'currency': raw}, 'sales_txn_quote', 'scenario')


def test_currency_inheritance_and_normalization():
    spec = config._coerce_sales_transaction_spec(
        {'currency': ' usd ', 'products': [{'sku': 'A'}, {'sku': 'B', 'currency': 'eur'}]},
        'sales_txn_quote', 'scenario')
    assert [p.currency for p in spec.products] == ['USD', 'EUR']
    short = config._coerce_sales_transaction_spec({'product': 'SKU', 'currency': 'eur'}, 'sales_txn_quote', 'scenario')
    assert short.products[0].currency == 'EUR'


def spec(products):
    return config.ScenarioSpec(None, products, 'quote_placed', False, None, 1)


@pytest.mark.parametrize('pin,expected', [(None, 'USD'), ('EUR', 'EUR')])
def test_resolve_spec_uses_account_default_or_override(fake_client, org_context, pin, expected):
    org_context.billing_ready_accounts[0].currency_iso_code = 'USD'
    fake_client.query_responses = [[pbe('USD'), pbe('EUR')]]
    result = runner.resolve_spec(fake_client, org_context, spec([config.ProductOption('SKU', (1, 1), currency=pin)]))
    assert result.options[0].product.currency_iso_code == expected
    assert result.account.currency_iso_code == expected
    assert org_context.billing_ready_accounts[0].currency_iso_code == 'USD'


def test_auto_product_resolves_currency_against_full_product(fake_client, org_context):
    org_context.billing_ready_accounts[0].currency_iso_code = 'EUR'
    fake_client.query_responses = [[pbe('USD'), pbe('EUR')]]
    result = runner.resolve_spec(fake_client, org_context, spec([config.ProductOption(None, (1, 1))]))
    assert result.options[0].product.currency_iso_code == 'EUR'


def test_mixed_pool_rejected_before_writes(fake_client, org_context):
    fake_client.query_responses = [[pbe('USD')], [pbe('EUR')]]
    opts = [config.ProductOption('SKU', (1, 1), currency=c) for c in ['USD', 'EUR']]
    with pytest.raises(config.ConfigError, match='same currency'):
        runner.resolve_spec(fake_client, org_context, spec(opts))
    assert not fake_client.posts


def test_manifest_resume_preserves_pbe_currency_and_model(fake_client, term_product):
    product = replace(term_product, currency_iso_code='EUR', pricebook_entry_id='pbe-EUR-Annual', selling_model_name='Annual')
    manifest = SimpleNamespace(lines=[LineItem(product=product, quantity=1).to_manifest_record()])
    fake_client.query_responses = [[pbe('USD'), pbe('EUR'), pbe('EUR', suffix='duplicate')]]
    line = cli._lines_from_manifest(fake_client, manifest, currency='USD')[0]
    assert line.product.pricebook_entry_id == product.pricebook_entry_id
    assert line.product.currency_iso_code == 'EUR'


def test_legacy_manifest_uses_account_currency(fake_client):
    fake_client.query_responses = [[pbe('USD'), pbe('EUR')]]
    lines = cli._lines_from_manifest(fake_client, SimpleNamespace(lines=[{'sku': 'SKU', 'quantity': 1}]), 'EUR')
    assert lines[0].product.currency_iso_code == 'EUR'


@pytest.mark.parametrize('currency', ['EUR', None])
def test_transaction_headers_follow_selected_currency(fake_client, billable_account, term_product, currency):
    account = replace(billable_account, currency_iso_code=currency)
    fake_client.post_responses = [{'success': True, 'id': 'opp'}, {'isSuccess': True, 'salesTransactionId': 'quote'}, {'isSuccess': True, 'salesTransactionId': 'order'}]
    line = LineItem(product=replace(term_product, currency_iso_code=currency, selling_model_type="OneTime"), quantity=1)
    lifecycle.create_opportunity(fake_client, account, 'Prospecting', 'test')
    lifecycle.place_sales_transaction(fake_client, account, [line], 'pb', 'test')
    lifecycle.place_order_transaction(fake_client, account, [line], 'pb', 'test')
    headers = [fake_client.posts[0][1]] + [body['graph']['records'][0]['record'] for _, body in fake_client.posts[1:]]
    for header in headers:
        if currency:
            assert header['CurrencyIsoCode'] == currency
        else:
            assert 'CurrencyIsoCode' not in header


def test_auto_product_without_sku_uses_product_id(fake_client, org_context):
    org_context.products = [replace(org_context.products[0], sku=None)]
    org_context.billing_ready_accounts[0].currency_iso_code = 'EUR'
    row = pbe('EUR'); row['Product2']['StockKeepingUnit'] = None
    fake_client.query_responses = [[row]]
    result = runner.resolve_spec(fake_client, org_context, spec([config.ProductOption(None, (1, 1))]))
    assert result.options[0].product.currency_iso_code == 'EUR'
    assert f"Product2Id = '{org_context.products[0].id}'" in fake_client.queries[0]


def test_missing_original_pbe_does_not_silently_switch(fake_client):
    fake_client.query_responses = [[pbe('EUR')]]
    with pytest.raises(discovery.DiscoveryError, match='no longer has active PBE'):
        discovery.resolve_product(fake_client, 'SKU', pricebook_entry_id='deleted')


def test_step_context_uses_manifest_without_default_discovery(fake_client, org_context, monkeypatch):
    account = replace(org_context.default_account(), currency_iso_code='USD')
    manifest = SimpleNamespace(run_id='resume', lines=[{
        'sku': 'SKU', 'product_id': 'product', 'pricebook_entry_id': 'pbe-EUR-Annual',
        'currency': 'EUR', 'selling_model': 'Annual', 'quantity': 1}])
    fake_client.query_responses = [[pbe('USD'), pbe('EUR')]]
    def unexpected(*args):
        raise AssertionError('A persisted selection must not trigger default config discovery')
    monkeypatch.setattr(cli, 'load_scenarios', unexpected)
    args = SimpleNamespace(to_stage='quote_placed', with_opportunity=False, poll_timeout=30)
    ctx = cli._build_step_context(args, SimpleNamespace(kind='sales_txn_quote'),
                                  fake_client, org_context, account, manifest)
    assert ctx.account.currency_iso_code == 'EUR'
    assert ctx.lines[0].product.pricebook_entry_id == 'pbe-EUR-Annual'
    assert account.currency_iso_code == 'USD'


def test_explicit_null_currency_returns_to_account_default():
    result = config._coerce_sales_transaction_spec(
        {'currency': 'EUR', 'products': [{'sku': 'SKU', 'currency': None}]},
        'sales_txn_quote', 'scenario')
    assert result.products[0].currency is None


def test_pbe_resolution_reads_later_query_pages(monkeypatch):
    from scripts.txn_data_harness.auth import SfRestClient
    client = SfRestClient(alias='test', instance_url='https://example.invalid', access_token='test')
    paths = []
    def request(method, path, body=None):
        paths.append(path)
        if len(paths) == 1:
            return {'records': [pbe('USD')], 'nextRecordsUrl': '/services/data/v68.0/query/next'}
        return {'records': [pbe('EUR')], 'done': True}
    monkeypatch.setattr(client, '_request', request)
    assert discovery.resolve_product(client, 'SKU', currency='EUR').currency_iso_code == 'EUR'
    assert paths[1] == '/services/data/v68.0/query/next'


@pytest.mark.parametrize('probe', ['product', 'account'])
@pytest.mark.parametrize('field', ['CurrencyIsoCode', 'UnrelatedField'])
def test_currency_probe_uses_api_response_not_request_path(fake_client, probe, field):
    from scripts.txn_data_harness.auth import SfApiError
    calls = []
    error = SfApiError(400, f'INVALID_FIELD: No such column {field}',
                       'GET', '/query?q=SELECT+Id,CurrencyIsoCode+FROM+PricebookEntry')
    def query(sql):
        calls.append(sql)
        if len(calls) == 1:
            raise error
        row = pbe()
        row.pop('CurrencyIsoCode')
        return [row]
    fake_client.query = query
    def resolve():
        if probe == 'product':
            return discovery.resolve_product(fake_client, 'SKU')
        return discovery._account_currency_map(fake_client, ['account'])
    if field == 'UnrelatedField':
        with pytest.raises(SfApiError) as caught:
            resolve()
        assert caught.value is error
        assert len(calls) == 1
    elif probe == 'product':
        assert resolve().currency_iso_code is None
        assert len(calls) == 2
    else:
        assert resolve() == {}
        assert len(calls) == 1


@pytest.mark.parametrize('dry_run', [True, False])
def test_direct_generate_reports_mixed_currency_without_traceback(
        monkeypatch, capsys, fake_client, dry_run):
    from scripts.txn_data_harness import generate
    from scripts.txn_data_harness.discovery import Account
    account = Account(id='account', name='Account', currency_iso_code='USD')
    ctx = SimpleNamespace(default_account=lambda: account)
    fake_client.query_responses = [[pbe('USD')], [pbe('EUR')]]
    mixed = spec([config.ProductOption(sku='SKU', quantity=(1, 1), currency='USD'),
                  config.ProductOption(sku='SKU', quantity=(1, 1), currency='EUR')])
    monkeypatch.setattr(generate.SfRestClient, 'from_alias', lambda *a, **k: fake_client)
    monkeypatch.setattr(generate, 'discover', lambda *a, **k: ctx)
    monkeypatch.setattr(generate, 'load_scenarios', lambda args: [mixed])
    args = ['--org', 'test'] + (['--dry-run'] if dry_run else [])
    assert generate.main(args) == 4
    error = capsys.readouterr().err
    assert 'ERROR: bad config:' in error
    assert 'same currency' in error
    assert 'Traceback' not in error


@pytest.mark.parametrize('current_sku', ['RENAMED', None])
def test_manifest_product_identity_survives_sku_edit(fake_client, current_sku):
    row = pbe('EUR')
    row['Product2']['StockKeepingUnit'] = current_sku
    def query(sql):
        assert "Product2Id = 'product'" in sql
        assert "Product2.StockKeepingUnit =" not in sql
        return [row]
    fake_client.query = query
    manifest = SimpleNamespace(lines=[{
        'sku': 'OLD-SKU', 'product_id': 'product',
        'pricebook_entry_id': row['Id'], 'currency': 'EUR', 'quantity': 1,
    }])
    lines = cli._lines_from_manifest(fake_client, manifest, 'USD')
    assert lines[0].product.pricebook_entry_id == row['Id']
    assert lines[0].product.id == 'product'
    assert lines[0].product.sku == current_sku


@pytest.mark.parametrize('sku', ['SHARED-SKU', None])
def test_auto_product_preserves_discovered_identity(fake_client, org_context, sku):
    preferred = replace(org_context.products[0], sku=sku)
    org_context.products = [preferred]
    org_context.billing_ready_accounts[0].currency_iso_code = 'EUR'
    intended = pbe('EUR')
    intended['Product2Id'] = preferred.id
    intended['Product2']['StockKeepingUnit'] = sku
    other = pbe('EUR', suffix='wrong-product')
    other['Product2Id'] = 'other-product'
    other['Product2']['StockKeepingUnit'] = sku
    def query(sql):
        # Without the identity filter a duplicate SKU is ambiguous (or could
        # select the wrong product if only that product has the target PBE).
        if f"Product2Id = '{preferred.id}'" not in sql:
            return [other]
        assert "Product2.StockKeepingUnit =" not in sql
        return [intended]
    fake_client.query = query
    resolved = runner.resolve_spec(fake_client, org_context,
                                   spec([config.ProductOption(None, (1, 1))]))
    assert resolved.options[0].product.id == preferred.id
    assert resolved.options[0].product.pricebook_entry_id == intended['Id']


def test_large_billing_account_discovery_batches_all_lookups(fake_client):
    import re
    from urllib.parse import quote
    ids = [f'001{i:015d}' for i in range(2101)]
    calls = []
    def query(sql):
        if 'FROM BillingAccount' in sql:
            return [{'Id': 'ba'+a, 'AccountId': a, 'Account': {'Name': a}} for a in ids]
        batch = re.findall(r"'(001\d{15})'", sql)
        assert 0 < len(batch) <= 100
        assert len(quote(sql)) < 8000
        calls.append((sql, batch))
        if 'FROM Contact' in sql:
            assert 'ORDER BY CreatedDate DESC' in sql
            return [r for a in batch for r in [
                {'Id': 'new'+a, 'AccountId': a}, {'Id': 'old'+a, 'AccountId': a}]]
        if 'CurrencyIsoCode' in sql:
            return [{'Id': a, 'CurrencyIsoCode': 'EUR'} for a in batch]
        return [{'Id': a, 'BillingCity': a} for a in batch]
    fake_client.query = query
    accounts = discovery.discover_accounts(fake_client)
    assert {a.id for a in accounts} == set(ids)
    assert all(a.currency_iso_code == 'EUR' and a.bill_to_contact_id == 'new'+a.id
               and a.billing_address.city == a.id for a in accounts)
    assert len(calls) == 66  # 22 batches for each of three lookups


def test_id_batches_deduplicate_and_propagate_later_failure(fake_client):
    calls = []
    error = RuntimeError('later page failed')
    def query(sql):
        calls.append(sql)
        if len(calls) == 2:
            raise error
        return [{'Id': 'first'}]
    fake_client.query = query
    ids = [f'001{i:015d}' for i in range(101)]
    with pytest.raises(RuntimeError) as caught:
        discovery._query_id_batches(fake_client, 'SELECT Id FROM Account WHERE Id IN ({ids})', ids + ids)
    assert caught.value is error
    assert calls[0].count("'001") == 100
    assert calls[1].count("'001") == 1
