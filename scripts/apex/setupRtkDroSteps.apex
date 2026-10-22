// Idempotent Rentokil DRO step definitions. StepType picklist values in this org
// are AutoTask / ManualTask / Milestone (not "Field Installation").
Id userId = UserInfo.getUserId();
Map<String, Id> groups = new Map<String, Id>();
for (FulfillmentStepDefinitionGroup g : [
    SELECT Id, Name FROM FulfillmentStepDefinitionGroup
    WHERE Name IN ('Initial Pest Treatment', 'Pest Finance')
]) {
    groups.put(g.Name, g.Id);
}
if (groups.size() < 2) {
    System.debug('Missing pest fulfillment step groups; run insert_pest_dro_fsl_data first');
} else {
    Map<String, FulfillmentStepDefinition> byName = new Map<String, FulfillmentStepDefinition>();
    for (FulfillmentStepDefinition s : [
        SELECT Id, Name, FlowDefinitionName FROM FulfillmentStepDefinition
        WHERE Name IN (
            'Create Initial Treatment Work Order',
            'Initial Treatment Complete',
            'Start Pest Subscription Billing'
        )
    ]) {
        byName.put(s.Name, s);
    }

    List<FulfillmentStepDefinition> toInsert = new List<FulfillmentStepDefinition>();
    List<FulfillmentStepDefinition> toUpdate = new List<FulfillmentStepDefinition>();
    if (!byName.containsKey('Create Initial Treatment Work Order')) {
        toInsert.add(new FulfillmentStepDefinition(
            Name = 'Create Initial Treatment Work Order',
            StepDefinitionGroupId = groups.get('Initial Pest Treatment'),
            AssignedToId = userId,
            FlowDefinitionName = 'RLM_RTK_Create_Initial_Work_Order',
            ForcePlanFreezeDuringExecution = 'Never',
            IsSkipBranch = false,
            Scope = 'Plan',
            StepType = 'AutoTask',
            UsageType = 'Fulfillment'
        ));
    } else if (byName.get('Create Initial Treatment Work Order').FlowDefinitionName != 'RLM_RTK_Create_Initial_Work_Order') {
        FulfillmentStepDefinition s = byName.get('Create Initial Treatment Work Order');
        s.FlowDefinitionName = 'RLM_RTK_Create_Initial_Work_Order';
        toUpdate.add(s);
    }
    if (!byName.containsKey('Initial Treatment Complete')) {
        toInsert.add(new FulfillmentStepDefinition(
            Name = 'Initial Treatment Complete',
            StepDefinitionGroupId = groups.get('Initial Pest Treatment'),
            AssignedToId = userId,
            ForcePlanFreezeDuringExecution = 'Never',
            IsSkipBranch = false,
            Scope = 'Plan',
            StepType = 'ManualTask',
            UsageType = 'Fulfillment'
        ));
    }
    if (!byName.containsKey('Start Pest Subscription Billing')) {
        toInsert.add(new FulfillmentStepDefinition(
            Name = 'Start Pest Subscription Billing',
            StepDefinitionGroupId = groups.get('Pest Finance'),
            AssignedToId = userId,
            ForcePlanFreezeDuringExecution = 'Never',
            IsSkipBranch = false,
            Scope = 'Plan',
            StepType = 'Milestone',
            UsageType = 'Fulfillment'
        ));
    }
    insert toInsert;
    update toUpdate;

    Map<String, Id> stepIds = new Map<String, Id>();
    for (FulfillmentStepDefinition s : [
        SELECT Id, Name FROM FulfillmentStepDefinition
        WHERE Name IN (
            'Create Initial Treatment Work Order',
            'Initial Treatment Complete',
            'Start Pest Subscription Billing'
        )
    ]) {
        stepIds.put(s.Name, s.Id);
    }

    Set<String> existingDeps = new Set<String>();
    for (FulfillmentStepDependencyDef d : [
        SELECT Name FROM FulfillmentStepDependencyDef
        WHERE Name IN ('Create WO to Treatment Complete', 'Treatment Complete to Bill')
    ]) {
        existingDeps.add(d.Name);
    }
    List<FulfillmentStepDependencyDef> deps = new List<FulfillmentStepDependencyDef>();
    if (!existingDeps.contains('Create WO to Treatment Complete')) {
        deps.add(new FulfillmentStepDependencyDef(
            Name = 'Create WO to Treatment Complete',
            DependencyScope = 'Plan',
            FulfillmentStepDefinitionId = stepIds.get('Initial Treatment Complete'),
            DependsOnStepDefinitionId = stepIds.get('Create Initial Treatment Work Order'),
            IsCompensateInReverse = false
        ));
    }
    if (!existingDeps.contains('Treatment Complete to Bill')) {
        deps.add(new FulfillmentStepDependencyDef(
            Name = 'Treatment Complete to Bill',
            DependencyScope = 'Plan',
            FulfillmentStepDefinitionId = stepIds.get('Start Pest Subscription Billing'),
            DependsOnStepDefinitionId = stepIds.get('Initial Treatment Complete'),
            IsCompensateInReverse = false
        ));
    }
    insert deps;

    Id groupId = groups.get('Initial Pest Treatment');
    List<ProductFulfillmentScenario> scenarios = [
        SELECT Id, FulfillmentStepDefnGroupId FROM ProductFulfillmentScenario
        WHERE Product.StockKeepingUnit = 'RTK-DRO-FSL' AND FulfillmentStepDefnGroupId != :groupId
    ];
    for (ProductFulfillmentScenario sc : scenarios) {
        sc.FulfillmentStepDefnGroupId = groupId;
    }
    update scenarios;
    System.debug('setupRtkDroSteps complete');
}
