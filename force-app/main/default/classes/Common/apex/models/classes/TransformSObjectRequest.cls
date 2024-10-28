public with sharing class TransformSObjectRequest {
    public List<AbstractRecord> recordsToTransform {get; set;}

    public TransformSObjectRequest(List<AbstractRecord> recordsToTransform) {
        this.recordsToTransform = recordsToTransform;
    }
}