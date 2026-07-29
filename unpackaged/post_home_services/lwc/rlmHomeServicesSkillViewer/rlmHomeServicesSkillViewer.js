import { LightningElement } from 'lwc';
import SKILL_URL from '@salesforce/resourceUrl/RLM_HomeServices_Skills';

export default class RlmHomeServicesSkillViewer extends LightningElement {
    files = [
        { label: 'SKILL.md', description: 'Agent skill instructions and workflow guide' },
        { label: 'sf-objects-reference.md', description: 'Salesforce object field reference' },
        { label: 'upload-static-resource.sh', description: 'Static resource upload utility script' }
    ];

    get skillUrl() {
        return SKILL_URL;
    }

    downloadSkill() {
        window.open(SKILL_URL, '_blank');
    }
}