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
    static void noIdsReturnsOneBlankOutput() {
        List<String> result = run(new RLM_DetermineDROSourceType.droSourceInfo());

        Assert.areEqual(1, result.size(), 'Every input gets an output, or the calling flow faults');
        Assert.areEqual('', result[0], 'An input with no ids resolves to a blank source type');
    }

    @IsTest
    static void everyInputGetsItsOwnOutputInOrder() {
        RLM_DetermineDROSourceType.droSourceInfo first = new RLM_DetermineDROSourceType.droSourceInfo();
        first.recordId = fakeId(OrderItem.SObjectType, 1);
        RLM_DetermineDROSourceType.droSourceInfo second = new RLM_DetermineDROSourceType.droSourceInfo();
        second.recordId = fakeId(Order.SObjectType, 2);
        RLM_DetermineDROSourceType.droSourceInfo third = new RLM_DetermineDROSourceType.droSourceInfo();
        third.recordIds = new List<String>{ fakeId(Account.SObjectType, 3) };

        List<String> result = RLM_DetermineDROSourceType.returnDROSourceObjectType(
            new List<RLM_DetermineDROSourceType.droSourceInfo>{ first, second, third }
        );

        Assert.areEqual(3, result.size(), 'A bulk call gets one output per input');
        Assert.areEqual('OrderItem', result[0], 'The first output is for the first input');
        Assert.areEqual('Order', result[1], 'The second output is for the second input');
        Assert.areEqual('Accounts', result[2], 'The third output is for the third input');
    }

    @IsTest
    static void emptyInputListReturnsNoOutputs() {
        List<String> result = RLM_DetermineDROSourceType.returnDROSourceObjectType(
            new List<RLM_DetermineDROSourceType.droSourceInfo>()
        );

        Assert.isTrue(result.isEmpty(), 'No inputs, no outputs, and no exception');
    }

    @IsTest
    static void emptyRecordIdListReturnsBlankOutput() {
        RLM_DetermineDROSourceType.droSourceInfo info = new RLM_DetermineDROSourceType.droSourceInfo();
        info.recordIds = new List<String>();

        List<String> result = run(info);

        Assert.areEqual(1, result.size(), 'The input still gets an output');
        Assert.areEqual('', result[0], 'An empty recordIds list resolves to a blank source type');
    }

    @IsTest
    static void malformedRecordIdReturnsBlankOutputAndKeepsTheRestOfTheBatch() {
        RLM_DetermineDROSourceType.droSourceInfo bad = new RLM_DetermineDROSourceType.droSourceInfo();
        bad.recordId = 'not-an-id';
        RLM_DetermineDROSourceType.droSourceInfo good = new RLM_DetermineDROSourceType.droSourceInfo();
        good.recordId = fakeId(OrderItem.SObjectType, 1);

        List<String> result = RLM_DetermineDROSourceType.returnDROSourceObjectType(
            new List<RLM_DetermineDROSourceType.droSourceInfo>{ bad, good }
        );

        Assert.areEqual(2, result.size(), 'One output per input');
        Assert.areEqual('', result[0], 'A malformed id resolves to a blank source type');
        Assert.areEqual('OrderItem', result[1], 'A bad input does not spoil the others');
    }
}
