"""
Custom CumulusCI task to clean up settings files for dev scratch orgs.
Removes fields that are not available based on org features and edition.
"""
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Set, Optional

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class CleanupSettingsForDev(BaseTask):
    """Remove problematic settings fields for dev scratch orgs based on feature availability."""
    
    task_options: Dict[str, Dict[str, Any]] = {
        "path": {
            "description": "Path to settings files",
            "required": True
        },
        "remove_for_scratch": {
            "description": "Remove fields for scratch orgs (default: True)",
            "required": False
        }
    }
    
    def _run_task(self):
        path = self.options.get("path")
        remove_for_scratch = self.options.get("remove_for_scratch", True)
        
        # Only clean up for scratch orgs
        is_scratch = False
        org_features: Set[str] = set()
        org_config_file: Optional[str] = None
        
        try:
            if hasattr(self, 'org_config') and self.org_config:
                is_scratch = getattr(self.org_config, 'scratch', False)
                # Get config file path to read features
                if hasattr(self.org_config, 'config_file'):
                    org_config_file = self.org_config.config_file
                elif hasattr(self.org_config, 'config'):
                    org_config_file = getattr(self.org_config.config, 'config_file', None)
        except AttributeError:
            pass
        
        if not remove_for_scratch or not is_scratch:
            self.logger.info("Skipping settings cleanup - not a scratch org or cleanup disabled")
            return
        
        # Read features from scratch org definition file
        if org_config_file:
            org_features = self._read_org_features(org_config_file)
            self.logger.info(f"Detected {len(org_features)} features in org definition")
        else:
            # Fallback: Try to detect based on org name or username
            try:
                if hasattr(self.org_config, 'username'):
                    username = self.org_config.username
                    if 'enhanced' in username.lower():
                        # Try dev-enhanced.json
                        enhanced_config = Path.cwd() / "orgs" / "dev-enhanced.json"
                        if enhanced_config.exists():
                            org_features = self._read_org_features(str(enhanced_config))
                            self.logger.info(f"Detected {len(org_features)} features from dev-enhanced.json (fallback)")
            except (AttributeError, Exception) as e:
                self.logger.debug(f"Could not use fallback config detection: {e}")
        
        settings_path = Path(path) / "2_settings"
        
        if not settings_path.exists():
            self.logger.warning(f"Settings path does not exist: {settings_path}")
            return
        
        # Clean up EinsteinGpt.settings-meta.xml
        einstein_file = settings_path / "EinsteinGpt.settings-meta.xml"
        if einstein_file.exists():
            self._cleanup_einstein_settings(einstein_file, org_features)
        
        # Clean up Industries.settings-meta.xml
        industries_file = settings_path / "Industries.settings-meta.xml"
        if industries_file.exists():
            self._cleanup_industries_settings(industries_file, org_features)
        
        # Clean up Permission Set Groups
        psg_path = Path(path) / "3_permissionsetgroups"
        if psg_path.exists():
            self._cleanup_permission_set_groups(psg_path, org_features)
            
            # Manage RC_TSO in .forceignore based on tso flag
            self._manage_rc_tso_in_forceignore()
    
    def _read_org_features(self, config_file: str) -> Set[str]:
        """Read features from scratch org definition JSON file."""
        features = set()
        try:
            # Handle both absolute and relative paths
            if not os.path.isabs(config_file):
                # Try relative to project root
                project_root = Path.cwd()
                config_path = project_root / config_file
            else:
                config_path = Path(config_file)
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    features = set(config.get('features', []))
                    self.logger.debug(f"Read {len(features)} features from {config_path}")
            else:
                self.logger.warning(f"Config file not found: {config_path}")
        except Exception as e:
            self.logger.warning(f"Error reading org config file {config_file}: {e}")
        
        return features
    
    def _cleanup_einstein_settings(self, einstein_file: Path, org_features: Set[str]):
        """Clean up EinsteinGpt settings based on feature availability."""
        # AI Provider fields - only available with specific features
        # Note: Even with features enabled, these may not be deployable in all org types
        # So we remove all AI provider fields for safety (they can be configured manually in org)
        fields_to_remove = [
            "enableAIProviderAWSBedrock",
            "enableAIProviderAzureOpenAI", 
            "enableAIProviderGoogleVertex",
            "enableAIProviderOpenAI"
        ]
        
        for field in fields_to_remove:
            self._remove_element_from_xml(einstein_file, field)
            self.logger.debug(f"Removed {field} (AI provider fields not deployable via metadata)")
    
    def _cleanup_industries_settings(self, industries_file: Path, org_features: Set[str]):
        """Clean up Industries settings based on feature availability."""
        # Map settings fields to required features
        fields_to_check = {
            # CLM-related fields
            "enableContractSearchPref": "ContractsAIClauseDesigner",  # May need CLM
            "enableContractsAIPref": "ContractsAIClauseDesigner",  # Requires CLM
            # Analytics/Scoring fields
            "enableScoringFrameworkOrgPref": "CGAnalytics",  # Requires CGAnalytics
            "enableScoringFrameworkCRMAPref": "CGAnalytics",  # Requires CGAnalytics
            # Disclosure framework
            "enableGnrcDisclsFrmwrk": "DisclosureFramework",  # Requires DisclosureFramework
            "enableTurnOffDsclsReprtPbsrName": "DisclosureFramework",  # Requires DisclosureFramework
            # AI/Intelligence fields
            "enableAIAccelerator": "RevenueIntelligence",  # May require RevenueIntelligence
            # Information library
            "enableInformationLibrary": "InsightsPlatform",  # Requires InsightsPlatform
        }
        
        for field, required_feature in fields_to_check.items():
            if required_feature not in org_features:
                self._remove_element_from_xml(industries_file, field)
            else:
                self.logger.debug(f"Keeping {field} - {required_feature} feature enabled")
    
    def _cleanup_permission_set_groups(self, psg_path: Path, org_features: Set[str]):
        """Move permission sets from permission set groups to RC_TSO based on feature availability."""
        # Map permission sets to required features
        # Permission sets that require specific features
        ps_feature_map = {
            # AI/Einstein permission sets - require AI features
            "force__AIAcceleratorPsl": "RevenueIntelligence",
            "force__EinsteinAssistantPsl": "Einstein1AIPlatform",
            "force__EinsteinGPTCallExplorerPsl": "Einstein1AIPlatform",
            "force__EinsteinGPTGetProductPricing": "Einstein1AIPlatform",
            "force__EinsteinGPTSalesCallSummaries": "Einstein1AIPlatform",
            "force__EinsteinGPTSalesEmails": "Einstein1AIPlatform",
            "force__EinsteinGPTSalesMiningPsl": "Einstein1AIPlatform",
            "force__EinsteinGPTSalesSummaries": "Einstein1AIPlatform",
            "force__EinsteinGPTSearchAnswers": "Einstein1AIPlatform",
            "force__EinsteinSearchAnswers": "Einstein1AIPlatform",
            # Analytics/Data Cloud permission sets
            "force__AnalyticsQueryService": "CGAnalytics",
            "force__EinsteinAnalyticsAdmin": "CGAnalytics",
            "force__EinsteinAnalyticsPlusAdmin": "CGAnalytics",
            "force__CGAnalyticsAdmin": "CGAnalytics",
            # CLM permission sets
            "force__ContractsAIClauseDesigner": "ContractsAIClauseDesigner",
            "force__ContractsAIRuntimeUser": "ContractsAIClauseDesigner",
            "force__CLMAnalyticsAdmin": "ContractsAIClauseDesigner",
        }
        
        # Permission sets that are never available in Enterprise dev scratch orgs
        # (regardless of features) - these will be moved to RC_TSO
        always_move_to_tso = {
            "force__CallCoachingIncluded",
            "force__CallCoachingUserPsl",
            "force__EinsteinARForConversations",
            "force__EinsteinActivityCaptureIncluded",
            "force__EinsteinAgentCWU",
            "force__EinsteinCopilotReviewMyDay",
            "force__EinsteinDiscoveryInTableau",
            "force__EinsteinPredictionsManagerAdmin",
            "force__EinsteinReplyRecommendations",
            "force__EinsteinSendMeetingRequestCopilot",
            "force__EinsteinServiceInnovations",
            "force__HighVelocitySalesCadenceCreatorIncluded",
            "force__HighVelocitySalesQuickCadenceCreatorIncluded",
            "force__HighVelocitySalesUserIncluded",
            "force__InboxIncluded",
            "force__MetadataStudioUser",
            "force__PipelineInspectionIncluded",
            "force__PrismBackofficeUser",
            "force__PrismPlaygroundUser",
            "force__SalesActionReviewBuyingCommittee",
            "force__SalesCloudEinsteinIncluded",
            "force__SalesCloudUnlimitedIncluded",
            "force__SalesMeetingsIncluded",
            "force__CDPAdmin",
            "force__DataCloudMtrcsVisualizationPsl",
            "force__GenieAdmin",
            "force__QueryForDataPipelines",
            "force__TableauEinsteinAdmin",
            "force__TableauEinsteinAnalyst",
            "force__TableauEinsteinIncludedAppBusinessUser",
            "force__TableauIncludedAppManager",
            "force__TableauUser",
            "force__NLPServicePsl"
        }
        
        # Collect all permission sets to move to RC_TSO
        permission_sets_to_move: Set[str] = set()
        
        # First pass: collect all permission sets that should be moved
        for psg_file in psg_path.glob("*.permissionsetgroup-meta.xml"):
            # Skip RC_TSO itself
            if psg_file.name == "RC_TSO.permissionsetgroup-meta.xml":
                continue
                
            try:
                tree = ET.parse(psg_file)
                root = tree.getroot()
                
                # Handle XML namespace
                ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
                if ns:
                    permission_sets = root.findall(".//ns:permissionSets", ns)
                else:
                    permission_sets = root.findall(".//permissionSets")
                
                for ps_elem in permission_sets:
                    ps_name = ps_elem.text
                    if not ps_name:
                        continue
                    
                    should_move = False
                    
                    # Check if always moved (regardless of features)
                    if ps_name in always_move_to_tso:
                        should_move = True
                    # Check feature requirements
                    # Note: Even if features are detected, these permission sets typically
                    # require additional licenses beyond just the feature being enabled.
                    # We move them all to RC_TSO for safety - they can be deployed when tso=true.
                    elif ps_name in ps_feature_map:
                        should_move = True
                    
                    if should_move:
                        permission_sets_to_move.add(ps_name)
                        
            except Exception as e:
                self.logger.warning(f"Error processing permission set group {psg_file}: {e}")
        
        # Second pass: remove permission sets from original PSGs and track what was moved
        for psg_file in psg_path.glob("*.permissionsetgroup-meta.xml"):
            # Skip RC_TSO itself
            if psg_file.name == "RC_TSO.permissionsetgroup-meta.xml":
                continue
                
            try:
                tree = ET.parse(psg_file)
                root = tree.getroot()
                
                # Handle XML namespace
                ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
                if ns:
                    permission_sets = root.findall(".//ns:permissionSets", ns)
                else:
                    permission_sets = root.findall(".//permissionSets")
                
                removed_count = 0
                
                for ps_elem in permission_sets[:]:
                    ps_name = ps_elem.text
                    if not ps_name or ps_name not in permission_sets_to_move:
                        continue
                    
                    # Remove from current PSG
                    parent = root
                    # Find the parent element
                    for elem in root.iter():
                        if ps_elem in list(elem):
                            parent = elem
                            break
                    parent.remove(ps_elem)
                    removed_count += 1
                    self.logger.info(f"Moved permission set {ps_name} from {psg_file.name} to RC_TSO")
                
                if removed_count > 0:
                    # Preserve original namespace format
                    ET.register_namespace('', 'http://soap.sforce.com/2006/04/metadata')
                    tree.write(psg_file, encoding='utf-8', xml_declaration=True, default_namespace='http://soap.sforce.com/2006/04/metadata')
                    self.logger.info(f"Moved {removed_count} permission set(s) from {psg_file.name} to RC_TSO")
                    
            except Exception as e:
                self.logger.warning(f"Error processing permission set group {psg_file}: {e}")
        
        # Create or update RC_TSO permission set group
        if permission_sets_to_move:
            self._create_or_update_tso_psg(psg_path, permission_sets_to_move)
    
    def _create_or_update_tso_psg(self, psg_path: Path, permission_sets: Set[str]):
        """Create or update RC_TSO permission set group with moved permission sets."""
        tso_file = psg_path / "RC_TSO.permissionsetgroup-meta.xml"
        namespace = 'http://soap.sforce.com/2006/04/metadata'
        
        try:
            if tso_file.exists():
                # Update existing RC_TSO
                tree = ET.parse(tso_file)
                root = tree.getroot()
                
                # Get existing permission sets
                ns = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
                if ns:
                    existing_ps = {elem.text for elem in root.findall(".//ns:permissionSets", ns) if elem.text}
                else:
                    existing_ps = {elem.text for elem in root.findall(".//permissionSets") if elem.text}
                
                # Add new permission sets that aren't already there
                new_ps = permission_sets - existing_ps
                
                if new_ps:
                    # Find the parent element for permission sets (usually PermissionSetGroup)
                    for elem in root.iter():
                        if elem.tag.endswith('PermissionSetGroup'):
                            for ps_name in sorted(new_ps):
                                ps_elem = ET.SubElement(elem, 'permissionSets')
                                ps_elem.text = ps_name
                            break
                    
                    ET.register_namespace('', namespace)
                    tree.write(tso_file, encoding='utf-8', xml_declaration=True, default_namespace=namespace)
                    self.logger.info(f"Added {len(new_ps)} permission set(s) to existing RC_TSO")
                else:
                    self.logger.debug("All permission sets already exist in RC_TSO")
            else:
                # Create new RC_TSO
                # Register namespace first
                ET.register_namespace('', namespace)
                root = ET.Element(f'{{{namespace}}}PermissionSetGroup')
                
                # Add standard PSG elements
                description = ET.SubElement(root, f'{{{namespace}}}description')
                description.text = 'Trialforce Source Org permission sets - moved from other PSGs based on feature availability'
                
                has_activation = ET.SubElement(root, f'{{{namespace}}}hasActivationRequired')
                has_activation.text = 'false'
                
                label = ET.SubElement(root, f'{{{namespace}}}label')
                label.text = 'RC_TSO'
                
                # Add permission sets
                for ps_name in sorted(permission_sets):
                    ps_elem = ET.SubElement(root, f'{{{namespace}}}permissionSets')
                    ps_elem.text = ps_name
                
                # Write the file with proper formatting
                tree = ET.ElementTree(root)
                ET.register_namespace('', namespace)
                tree.write(tso_file, encoding='utf-8', xml_declaration=True, default_namespace=namespace)
                # Reformat with proper indentation
                ET.indent(tree, space="    ")
                tree.write(tso_file, encoding='utf-8', xml_declaration=True, default_namespace=namespace)
                self.logger.info(f"Created RC_TSO permission set group with {len(permission_sets)} permission set(s)")
                
        except Exception as e:
            self.logger.warning(f"Error creating/updating RC_TSO permission set group: {e}")
    
    def _remove_element_from_xml(self, xml_file: Path, element_name: str):
        """Remove a specific element from an XML file."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            element_to_remove = None
            for child in root:
                if child.tag.endswith(element_name) or child.tag.split('}')[-1] == element_name:
                    element_to_remove = child
                    break
            
            if element_to_remove is not None:
                root.remove(element_to_remove)
                # Preserve default namespace format
                ET.register_namespace('', 'http://soap.sforce.com/2006/04/metadata')
                tree.write(xml_file, encoding='utf-8', xml_declaration=True, default_namespace='http://soap.sforce.com/2006/04/metadata')
                self.logger.info(f"Removed {element_name} from {xml_file.name}")
            else:
                self.logger.debug(f"Element {element_name} not found in {xml_file.name}")
                       
        except Exception as e:
            self.logger.warning(f"Error processing {xml_file}: {e}")
    
    def _manage_rc_tso_in_forceignore(self):
        """Add or remove RC_TSO from .forceignore based on tso flag."""
        # Check if tso flag is enabled using CumulusCI project config format
        tso_enabled = False
        try:
            if hasattr(self, 'project_config') and self.project_config:
                # Access custom project config using CumulusCI format: project__custom__tso
                tso_enabled = getattr(self.project_config, 'project__custom__tso', False)
                # Also try alternative access pattern
                if not tso_enabled:
                    try:
                        custom = getattr(self.project_config, 'project', {}).get('custom', {})
                        tso_enabled = custom.get('tso', False)
                    except (AttributeError, KeyError, TypeError):
                        pass
        except (AttributeError, KeyError) as e:
            self.logger.debug(f"Could not read tso flag from project config: {e}, defaulting to False")
        
        self.logger.info(f"tso flag is {'enabled' if tso_enabled else 'disabled'}")
        
        forceignore_path = Path.cwd() / ".forceignore"
        if not forceignore_path.exists():
            self.logger.warning(".forceignore file not found, skipping RC_TSO management")
            return
        
        rc_tso_entry = "unpackaged/pre/3_permissionsetgroups/RC_TSO.permissionsetgroup-meta.xml"
        rc_tso_comment = "# RC_TSO - Storage only, never deployed (preserves permission sets that aren't available in dev orgs)"
        
        try:
            # Read current .forceignore
            with open(forceignore_path, 'r') as f:
                lines = f.readlines()
            
            # Find all RC_TSO entries (both active and commented)
            rc_tso_entry_indices = []
            rc_tso_comment_indices = []
            
            for i, line in enumerate(lines):
                # Check for the actual entry (not commented)
                if rc_tso_entry in line and not line.strip().startswith('#'):
                    rc_tso_entry_indices.append(i)
                # Check for commented entry
                elif rc_tso_entry in line and line.strip().startswith('#'):
                    rc_tso_entry_indices.append(i)
                # Check for comment lines
                if "RC_TSO" in line and line.strip().startswith('#'):
                    rc_tso_comment_indices.append(i)
            
            # Determine what to do
            if tso_enabled:
                # tso=true: Remove RC_TSO from .forceignore (allow deployment)
                # Remove all RC_TSO entries and associated comments
                if rc_tso_entry_indices or rc_tso_comment_indices:
                    # Remove in reverse order to maintain indices
                    indices_to_remove = sorted(set(rc_tso_entry_indices + rc_tso_comment_indices), reverse=True)
                    for idx in indices_to_remove:
                        lines.pop(idx)
                    
                    with open(forceignore_path, 'w') as f:
                        f.writelines(lines)
                    self.logger.info("RC_TSO removed from .forceignore (tso=true - will be deployed)")
                else:
                    self.logger.debug("RC_TSO not in .forceignore (tso=true - will be deployed)")
            else:
                # tso=false: Add RC_TSO to .forceignore (exclude from deployment)
                # Check if there's already an active (non-commented) entry
                has_active_entry = any(
                    rc_tso_entry in lines[i] and not lines[i].strip().startswith('#')
                    for i in rc_tso_entry_indices
                )
                
                if not has_active_entry:
                    # Find the PSGs section or add at end
                    psg_section_index = -1
                    for i, line in enumerate(lines):
                        if "# PSGs" in line or "#unpackaged/pre/3_permissionsetgroups" in line:
                            psg_section_index = i
                            break
                    
                    if psg_section_index >= 0:
                        # Insert after PSGs section comment
                        insert_index = psg_section_index + 1
                        # Find the next line after PSGs section (skip commented lines)
                        for i in range(psg_section_index + 1, len(lines)):
                            if lines[i].strip() and not lines[i].strip().startswith('#'):
                                insert_index = i
                                break
                            elif not lines[i].strip():
                                # Blank line - good place to insert
                                insert_index = i + 1
                                break
                        # Insert comment and entry
                        lines.insert(insert_index, f"{rc_tso_comment}\n")
                        lines.insert(insert_index + 1, f"{rc_tso_entry}\n")
                    else:
                        # Add at end
                        if lines and not lines[-1].endswith('\n'):
                            lines[-1] += '\n'
                        lines.append(f"\n{rc_tso_comment}\n")
                        lines.append(f"{rc_tso_entry}\n")
                    
                    with open(forceignore_path, 'w') as f:
                        f.writelines(lines)
                    self.logger.info("RC_TSO added to .forceignore (tso=false - excluded from deployment)")
                else:
                    self.logger.debug("RC_TSO already in .forceignore (tso=false)")
                    
        except Exception as e:
            self.logger.warning(f"Error managing RC_TSO in .forceignore: {e}")