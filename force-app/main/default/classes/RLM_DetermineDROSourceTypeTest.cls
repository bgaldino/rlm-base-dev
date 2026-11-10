@IsTest
private class RLM_DetermineDROSourceTypeTest {

    private static String fakeId(Schema.SObjectType objectType, Integer n) {
        return objectType.getDescribe().getKeyPrefix() + String.valueOf(n).leftPad(12, '0');
    }

    private static List<String> run(RLM_DetermineDROSourceType.droSourceInfo info) {
        return RLM_DetermineDROSourceType.returnDROSourceObjectType(
            new List<RLM_DetermineDROSourceType.droSourceInfo>{ info }
        );
    }

    @IsTest
    static void singleRecordIdReturnsItsObjectName() {
        RLM_DetermineDROSourceType.droSourceInfo info = new RLM_DetermineDROSourceType.droSourceInfo();
        info.recordId = fakeId(OrderItem.SObjectType, 1);

        List<String> result = run(info);

        Assert.areEqual(1, result.size(), 'One source type is returned');
        Assert.areEqual('OrderItem', result[0], 'A single record id resolves to its object name');
    }

    @IsTest
    static void recordIdListReturnsPluralObjectNameOfFirstId() {
        RLM_DetermineDROSourceType.droSourceInfo info = new RLM_DetermineDROSourceType.droSourceInfo();
        info.recordIds = new List<String>{
            fakeId(Order.SObjectType, 1),
            fakeId(Account.SObjectType, 2)
        };

        List<String> result = run(info);

        Assert.areEqual(1, result.size(), 'One source type is returned');
        Assert.areEqual('Orders', result[0], 'A record id list resolves to the first id\'s object name, pluralised');
    }

    @IsTest
    static void singleRecordIdTakesPrecedenceOverList() {
        RLM_DetermineDROSourceType.droSourceInfo info = new RLM_DetermineDROSourceType.droSourceInfo();
        info.recordId = fakeId(OrderItem.SObjectType, 1);
        info.recordIds = new List<String>{ fakeId(Order.SObjectType, 1) };

        List<String> result = run(info);

        Assert.areEqual(1, result.size(), 'Only one branch runs');
        Assert.areEqual('OrderItem', result[0], 'recordId wins when both inputs are set');
    }

    @IsTest
    static void noIdsReturnsEmptyList() {
        List<String> result = run(new RLM_DetermineDROSourceType.droSourceInfo());

        Assert.isTrue(result.isEmpty(), 'No input ids yields no source type');
    }

    @IsTest
    static void onlyTheFirstInputIsRead() {
        RLM_DetermineDROSourceType.droSourceInfo first = new RLM_DetermineDROSourceType.droSourceInfo();
        first.recordId = fakeId(OrderItem.SObjectType, 1);
        RLM_DetermineDROSourceType.droSourceInfo second = new RLM_DetermineDROSourceType.droSourceInfo();
        second.recordId = fakeId(Order.SObjectType, 2);

        List<String> result = RLM_DetermineDROSourceType.returnDROSourceObjectType(
            new List<RLM_DetermineDROSourceType.droSourceInfo>{ first, second }
        );

        Assert.areEqual(
            1, result.size(),
            'Known gap: only the first of several inputs is read, so a bulk call gets one output; '
                + 'update this test when it is fixed'
        );
        Assert.areEqual('OrderItem', result[0], 'The output is for the first input');
    }

    @IsTest
    static void emptyInputListThrows() {
        try {
            RLM_DetermineDROSourceType.returnDROSourceObjectType(new List<RLM_DetermineDROSourceType.droSourceInfo>());
            Assert.fail(
                'Known gap: an empty input list throws a raw ListException; update this test when it is fixed'
            );
        } catch (ListException e) {
            Assert.isTrue(
                e.getMessage().contains('out of bounds'),
                'The missing first input is indexed: ' + e.getMessage()
            );
        }
    }

    @IsTest
    static void emptyRecordIdListThrows() {
        RLM_DetermineDROSourceType.droSourceInfo info = new RLM_DetermineDROSourceType.droSourceInfo();
        info.recordIds = new List<String>();

        try {
            run(info);
            Assert.fail(
                'Known gap: an empty recordIds list throws a raw ListException; update this test when it is fixed'
            );
        } catch (ListException e) {
            Assert.isTrue(
                e.getMessage().contains('out of bounds'),
                'The missing first id is indexed: ' + e.getMessage()
            );
        }
    }

    @IsTest
    static void malformedRecordIdThrows() {
        RLM_DetermineDROSourceType.droSourceInfo info = new RLM_DetermineDROSourceType.droSourceInfo();
        info.recordId = 'not-an-id';

        try {
            run(info);
            Assert.fail(
                'Known gap: a malformed record id throws a raw StringException; update this test when it is fixed'
            );
        } catch (StringException e) {
            Assert.isTrue(e.getMessage().contains('not-an-id'), 'The invalid id is named: ' + e.getMessage());
        }
    }
}
