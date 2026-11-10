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
    static void malformedRecordIdThrows() {
        RLM_DetermineDROSourceType.droSourceInfo info = new RLM_DetermineDROSourceType.droSourceInfo();
        info.recordId = 'not-an-id';

        try {
            run(info);
            Assert.fail('A malformed record id must not resolve to a source type');
        } catch (StringException e) {
            Assert.isNotNull(e.getMessage(), 'The invalid id is reported');
        }
    }
}
