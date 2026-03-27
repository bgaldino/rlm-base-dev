#!/usr/bin/env python3
"""
build_erds.py — Generate Entity Relationship Diagrams from RLM JSON schemas.

Reads three JSON domain files and generates:
1. Individual domain Mermaid ERDs (per-domain .mermaid files)
2. A master Mermaid ERD (cross-domain, high-level)
3. An interactive HTML D3.js force-directed graph viewer

Output: /docs/erds/{domain}.mermaid, master.mermaid, revenue-cloud-erd.html
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class ERDBuilder:
    """Build Entity Relationship Diagrams from JSON schema files."""

    # Domain color palette for HTML visualization
    DOMAIN_COLORS = {
        "PCM": "#FF6B6B",
        "Pricing": "#4ECDC4",
        "RateManagement": "#45B7D1",
        "Configurator": "#FFA07A",
        "TransactionManagement": "#98D8C8",
        "DRO": "#F7DC6F",
        "UsageManagement": "#BB8FCE",
        "Billing": "#85C1E2",
    }

    def __init__(self, output_dir: str = "docs/erds"):
        """Initialize ERD builder with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.all_objects = {}  # {object_name: (domain, object_data)}
        self.all_relationships = []  # List of (source, target, field, type)
        self.domain_objects = defaultdict(list)  # {domain: [objects]}
        self.objects_by_domain = defaultdict(list)  # For stats

    def load_json_files(self, file_paths: List[str]) -> Dict:
        """Load and merge JSON files from multiple sources."""
        all_data = {}

        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Merge into all_data (each file has domain keys)
                    for domain, content in data.items():
                        all_data[domain] = content
                    print(f"✓ Loaded {file_path}")
            except Exception as e:
                print(f"✗ Error loading {file_path}: {e}", file=sys.stderr)
                return None

        return all_data

    def normalize_domain_names(self, data: Dict) -> Dict:
        """Normalize domain names to match the expected format."""
        normalized = {}
        domain_map = {
            "PCM": "PCM",
            "Pricing": "Pricing",
            "RateManagement": "RateManagement",
            "Configurator": "Configurator",
            "TransactionManagement": "TransactionManagement",
            "DRO": "DRO",
            "UsageManagement": "UsageManagement",
            "Billing": "Billing",
        }

        for key, value in data.items():
            if key in domain_map:
                normalized[domain_map[key]] = value
            else:
                normalized[key] = value

        return normalized

    def build_object_map(self, data: Dict):
        """Build a map of all objects and their relationships."""
        for domain, content in data.items():
            objects = content.get("objects", [])

            for obj in objects:
                name = obj.get("name")
                if name:
                    self.all_objects[name] = (domain, obj)
                    self.domain_objects[domain].append(obj)
                    self.objects_by_domain[domain].append(name)

                    # Index relationships
                    relationships = obj.get("relationships", [])
                    for rel in relationships:
                        target = rel.get("target")
                        field = rel.get("field")
                        rel_type = rel.get("type", "Lookup")

                        if target and field:
                            self.all_relationships.append((name, target, field, rel_type))

    def get_relationship_type_for_mermaid(self, rel_type: str) -> str:
        """Convert relationship type to Mermaid notation."""
        # Mermaid notation:
        # ||--o{ : one-to-many
        # ||--|| : one-to-one
        # }o--|| : many-to-one
        if rel_type == "Lookup":
            return "}o--||"  # Many-to-one (child to parent)
        elif rel_type == "Master-Detail":
            return "||--o{"  # One-to-many (parent to child)
        else:
            return "}o--||"  # Default to many-to-one

    def generate_domain_erd(self, domain: str, objects: List[Dict], domain_display_name: str):
        """Generate Mermaid ERD for a single domain."""
        if not objects:
            return

        lines = ["erDiagram"]

        # Add entities with key fields
        for obj in objects:
            name = obj.get("name")
            if name:
                # Get relationship field names for this object
                rel_fields = [rel.get("field") for rel in obj.get("relationships", []) if rel.get("field")]

                # Add the entity line (optionally with fields)
                if rel_fields:
                    # Include relationship field names as attributes
                    fields_str = ", ".join(rel_fields[:5])  # Limit to first 5 fields
                    lines.append(f'    {name} {{ string {fields_str} }}')
                else:
                    lines.append(f'    {name}')

        # Add relationships
        added_rels = set()  # Track to avoid duplicates
        for obj in objects:
            source = obj.get("name")
            for rel in obj.get("relationships", []):
                target = rel.get("target")
                field = rel.get("field")
                rel_type = rel.get("type", "Lookup")

                # Only include relationships where both objects are in this domain
                if target and source in [o.get("name") for o in objects]:
                    if target in [o.get("name") for o in objects]:
                        rel_key = (min(source, target), max(source, target), field)
                        if rel_key not in added_rels:
                            mermaid_type = self.get_relationship_type_for_mermaid(rel_type)
                            lines.append(f'    {source} {mermaid_type} {target} : {field}')
                            added_rels.add(rel_key)

        # Write to file
        domain_file = self.output_dir / f"{self._domain_to_filename(domain_display_name)}.mermaid"
        with open(domain_file, 'w') as f:
            f.write('\n'.join(lines))

        print(f"✓ Generated {domain_file.name} ({len(objects)} objects)")

    def _domain_to_filename(self, domain_name: str) -> str:
        """Convert domain name to filename."""
        mapping = {
            "PCM": "pcm",
            "Pricing": "pricing",
            "RateManagement": "rate-management",
            "Configurator": "configurator",
            "TransactionManagement": "transaction-management",
            "DRO": "dro",
            "UsageManagement": "usage-management",
            "Billing": "billing",
        }
        return mapping.get(domain_name, domain_name.lower().replace(" ", "-"))

    def generate_master_erd(self, data: Dict):
        """Generate high-level master ERD showing cross-domain relationships."""
        lines = ["erDiagram"]

        # Create domain super-entities with their key objects
        domain_key_objects = {
            "PCM": ["Product2", "ProductAttributeDefinition", "ProductFamily"],
            "Pricing": ["PriceBook2", "PriceBookEntry", "PriceAdjustment"],
            "RateManagement": ["RateCard", "RateCardEntry", "RateCardLookupEntry"],
            "Configurator": ["ProductConfigurationFlow", "ExpressionSet"],
            "TransactionManagement": ["Asset", "AssetStatePeriod", "Order", "OrderItem"],
            "DRO": ["DROTransaction", "DROMessageSet", "DROOutboundMessage"],
            "UsageManagement": ["ProductUsageGrant", "ProductUsageResource", "UsageRecord"],
            "Billing": ["BillingSchedule", "Invoice", "InvoiceLine", "BillingScheduleVersion"],
        }

        # Add all domain entities as entity declarations
        for domain in sorted(domain_key_objects.keys()):
            for obj in domain_key_objects[domain]:
                if obj in self.all_objects:
                    lines.append(f'    {obj}')

        # Track added relationships to avoid duplicates
        added_rels = set()

        # Add key cross-domain relationships
        cross_domain_relationships = [
            ("OrderItem", "Product2", "Product2Id", "Lookup"),
            ("PriceBookEntry", "Product2", "Product2Id", "Lookup"),
            ("PriceBookEntry", "PriceBook2", "Pricebook2Id", "Lookup"),
            ("Asset", "Product2", "Product2Id", "Lookup"),
            ("Asset", "Account", "AccountId", "Lookup"),
            ("Order", "Account", "AccountId", "Lookup"),
            ("Invoice", "Order", "OrderId", "Lookup"),
            ("BillingSchedule", "Order", "OrderId", "Lookup"),
            ("DROTransaction", "Order", "OrderId", "Lookup"),
            ("ProductUsageGrant", "Asset", "AssetId", "Lookup"),
            ("ProductUsageGrant", "Product2", "ProductOfferId", "Lookup"),
            ("RateCard", "Product2", "ProductId", "Lookup"),
            ("AssetStatePeriod", "Asset", "AssetId", "Lookup"),
        ]

        for source, target, field, rel_type in cross_domain_relationships:
            if source in self.all_objects and target in self.all_objects:
                rel_key = (min(source, target), max(source, target))
                if rel_key not in added_rels:
                    mermaid_type = self.get_relationship_type_for_mermaid(rel_type)
                    lines.append(f'    {source} {mermaid_type} {target} : {field}')
                    added_rels.add(rel_key)

        # Write master ERD
        master_file = self.output_dir / "master.mermaid"
        with open(master_file, 'w') as f:
            f.write('\n'.join(lines))

        print(f"✓ Generated master.mermaid ({len(domain_key_objects)} domains, {len(added_rels)} relationships)")

    def generate_html_viewer(self, data: Dict):
        """Generate interactive HTML D3.js force-directed graph viewer."""
        # Prepare data for D3.js
        nodes = []
        links = []
        node_set = set()

        # Build nodes
        for obj_name, (domain, obj) in self.all_objects.items():
            if obj_name not in node_set:
                rel_count = len(obj.get("relationships", []))
                nodes.append({
                    "id": obj_name,
                    "domain": domain,
                    "relationshipCount": rel_count,
                })
                node_set.add(obj_name)

        # Build links (relationships)
        added_links = set()
        for source, target, field, rel_type in self.all_relationships:
            if source in node_set and target in node_set:
                link_key = (min(source, target), max(source, target))
                if link_key not in added_links:
                    links.append({
                        "source": source,
                        "target": target,
                        "field": field,
                        "type": rel_type,
                    })
                    added_links.add(link_key)

        # Calculate domain stats
        domain_stats = {}
        for domain in self.objects_by_domain:
            domain_stats[domain] = {
                "count": len(self.objects_by_domain[domain]),
                "color": self.DOMAIN_COLORS.get(domain, "#999999"),
            }

        # Generate HTML
        html_content = self._generate_html_template(nodes, links, domain_stats)

        html_file = self.output_dir / "revenue-cloud-erd.html"
        with open(html_file, 'w') as f:
            f.write(html_content)

        print(f"✓ Generated revenue-cloud-erd.html ({len(nodes)} objects, {len(links)} relationships)")

    def _generate_html_template(self, nodes: List, links: List, domain_stats: Dict) -> str:
        """Generate the HTML template with embedded D3.js visualization."""

        # Convert Python objects to JSON
        nodes_json = json.dumps(nodes)
        links_json = json.dumps(links)
        domain_stats_json = json.dumps(domain_stats)

        total_objects = len(nodes)
        total_relationships = len(links)

        # Calculate avg relationships
        avg_rel = total_relationships / len(domain_stats) if domain_stats else 0

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Revenue Cloud v66.0 — Entity Relationship Diagram</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
        }}

        .container {{
            display: flex;
            width: 100%;
            height: 100vh;
        }}

        .sidebar {{
            width: 280px;
            background: white;
            box-shadow: 2px 0 8px rgba(0,0,0,0.1);
            overflow-y: auto;
            padding: 20px;
            z-index: 100;
        }}

        .sidebar-header {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }}

        .stats-panel {{
            background: #f5f5f5;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }}

        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }}

        .stat-label {{
            color: #666;
            font-weight: 500;
        }}

        .stat-value {{
            font-weight: 700;
            color: #667eea;
        }}

        .domain-filters {{
            margin-top: 20px;
        }}

        .domain-filters-title {{
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 12px;
        }}

        .domain-checkbox {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            cursor: pointer;
        }}

        .domain-checkbox input {{
            margin-right: 8px;
            cursor: pointer;
            width: 16px;
            height: 16px;
        }}

        .domain-checkbox label {{
            cursor: pointer;
            flex: 1;
            font-size: 13px;
            color: #333;
        }}

        .domain-color {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 2px;
            margin-right: 6px;
        }}

        .domain-count {{
            font-size: 11px;
            color: #999;
            margin-left: auto;
        }}

        .search-box {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 20px;
        }}

        .search-box::placeholder {{
            color: #999;
        }}

        .legend {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}

        .legend-title {{
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 10px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-size: 12px;
        }}

        .legend-line {{
            width: 20px;
            height: 2px;
            margin-right: 8px;
        }}

        .legend-solid {{
            background: #333;
        }}

        .legend-dashed {{
            background: #999;
            background-image: linear-gradient(90deg, #999 50%, transparent 50%);
            background-size: 4px 2px;
        }}

        .main {{
            flex: 1;
            position: relative;
            background: #f9f9f9;
        }}

        .title-bar {{
            background: white;
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .title-bar h1 {{
            font-size: 20px;
            color: #333;
        }}

        svg {{
            width: 100%;
            height: calc(100vh - 55px);
            background: white;
        }}

        .node {{
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .node:hover {{
            stroke-width: 3px;
            filter: drop-shadow(0 0 8px rgba(0,0,0,0.3));
        }}

        .node.highlighted {{
            stroke: #ffd700;
            stroke-width: 3px;
            filter: drop-shadow(0 0 8px rgba(255,215,0,0.6));
        }}

        .link {{
            stroke: #999;
            stroke-opacity: 0.4;
            transition: all 0.2s;
        }}

        .link.lookup {{
            stroke-dasharray: 5,5;
        }}

        .link.highlighted {{
            stroke: #ffd700;
            stroke-opacity: 0.8;
            stroke-width: 2px;
        }}

        .node-label {{
            font-size: 11px;
            pointer-events: none;
            text-anchor: middle;
            fill: #333;
            font-weight: 500;
        }}

        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.85);
            color: white;
            padding: 10px 12px;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 250px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="sidebar-header">Revenue Cloud</div>

            <div class="stats-panel">
                <div class="stat-item">
                    <span class="stat-label">Total Objects</span>
                    <span class="stat-value">{total_objects}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Relationships</span>
                    <span class="stat-value">{total_relationships}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Domains</span>
                    <span class="stat-value">{len(domain_stats)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Avg per Domain</span>
                    <span class="stat-value">{avg_rel:.1f}</span>
                </div>
            </div>

            <input type="text" class="search-box" id="searchBox" placeholder="Search objects...">

            <div class="domain-filters">
                <div class="domain-filters-title">Domains</div>
                <div id="domainCheckboxes"></div>
            </div>

            <div class="legend">
                <div class="legend-title">Relationships</div>
                <div class="legend-item">
                    <div class="legend-line legend-solid"></div>
                    <span>Master-Detail</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line legend-dashed"></div>
                    <span>Lookup</span>
                </div>
            </div>
        </div>

        <div class="main">
            <div class="title-bar">
                <h1>Revenue Cloud v66.0 — Entity Relationship Diagram</h1>
            </div>
            <svg id="graph"></svg>
        </div>
    </div>

    <div class="tooltip" id="tooltip" style="display:none;"></div>

    <script>
        const data = {{
            nodes: {nodes_json},
            links: {links_json}
        }};

        const domainStats = {domain_stats_json};
        const domainColors = {json.dumps(self.DOMAIN_COLORS)};

        // Initialize domain checkboxes
        const domainCheckboxes = document.getElementById('domainCheckboxes');
        const domains = Object.keys(domainStats).sort();
        const activeDomains = new Set(domains);

        domains.forEach(domain => {{
            const div = document.createElement('div');
            div.className = 'domain-checkbox';

            const color = domainStats[domain].color;
            const count = domainStats[domain].count;

            div.innerHTML = `
                <input type="checkbox" id="domain-${{domain}}" checked>
                <label for="domain-${{domain}}">
                    <span class="domain-color" style="background: ${{color}}"></span>
                    <span>${{domain}}</span>
                    <span class="domain-count">(${{count}})</span>
                </label>
            `;

            const checkbox = div.querySelector('input');
            checkbox.addEventListener('change', () => {{
                if (checkbox.checked) {{
                    activeDomains.add(domain);
                }} else {{
                    activeDomains.delete(domain);
                }}
                updateVisualization();
            }});

            domainCheckboxes.appendChild(div);
        }});

        // Set up D3.js visualization
        const width = document.querySelector('.main').clientWidth;
        const height = window.innerHeight - 55;

        const svg = d3.select('#graph')
            .attr('width', width)
            .attr('height', height);

        // Create zoom behavior
        const zoom = d3.zoom()
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});

        svg.call(zoom);

        const g = svg.append('g');

        // Arrow marker definition
        svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('markerWidth', 10)
            .attr('markerHeight', 10)
            .attr('refX', 8)
            .attr('refY', 3)
            .attr('orient', 'auto')
            .append('polygon')
            .attr('points', '0 0, 10 3, 0 6')
            .attr('fill', '#999');

        // Simulation setup
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => 5 + (d.relationshipCount * 1.5)));

        // Create link elements
        const link = g.selectAll('line')
            .data(data.links)
            .enter()
            .append('line')
            .attr('class', d => 'link ' + (d.type === 'Lookup' ? 'lookup' : 'master-detail'))
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.4)
            .attr('stroke-width', 1.5);

        // Create node elements
        const node = g.selectAll('circle')
            .data(data.nodes)
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr('r', d => 4 + (d.relationshipCount * 1.2))
            .attr('fill', d => domainStats[d.domain].color)
            .call(d3.drag()
                .on('start', dragStarted)
                .on('drag', dragged)
                .on('end', dragEnded));

        // Add node labels
        const label = g.selectAll('text')
            .data(data.nodes)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('dy', '0.3em')
            .text(d => d.id);

        // Tooltip
        const tooltip = document.getElementById('tooltip');

        node.on('mouseover', function(event, d) {{
            tooltip.textContent = d.id + ' (' + d.domain + ') — ' + d.relationshipCount + ' relationships';
            tooltip.style.left = (event.pageX + 10) + 'px';
            tooltip.style.top = (event.pageY + 10) + 'px';
            tooltip.style.display = 'block';

            d3.select(this).classed('highlighted', true);

            link.classed('highlighted', l => l.source.id === d.id || l.target.id === d.id);
        }})
        .on('mousemove', function(event) {{
            tooltip.style.left = (event.pageX + 10) + 'px';
            tooltip.style.top = (event.pageY + 10) + 'px';
        }})
        .on('mouseout', function() {{
            tooltip.style.display = 'none';
            d3.select(this).classed('highlighted', false);
            link.classed('highlighted', false);
        }});

        // Search functionality
        const searchBox = document.getElementById('searchBox');
        let searchTerm = '';

        searchBox.addEventListener('input', (e) => {{
            searchTerm = e.target.value.toLowerCase();
            updateVisualization();
        }});

        function updateVisualization() {{
            node.style('opacity', d => {{
                if (!activeDomains.has(d.domain)) return 0;
                if (searchTerm && !d.id.toLowerCase().includes(searchTerm)) return 0.1;
                return 1;
            }});

            label.style('opacity', d => {{
                if (!activeDomains.has(d.domain)) return 0;
                if (searchTerm && !d.id.toLowerCase().includes(searchTerm)) return 0.1;
                return 1;
            }});

            link.style('opacity', d => {{
                if (!activeDomains.has(d.source.domain) || !activeDomains.has(d.target.domain)) return 0;
                if (searchTerm && !d.source.id.toLowerCase().includes(searchTerm) && !d.target.id.toLowerCase().includes(searchTerm)) {{
                    return 0.05;
                }}
                return 0.4;
            }});
        }}

        // Update positions on simulation tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});

        // Drag functions
        function dragStarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragEnded(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
"""
        return html

    def run(self, json_files: List[str]):
        """Main entry point to build all ERDs."""
        print(f"\n{'='*60}")
        print(f"RLM Entity Relationship Diagram Builder")
        print(f"{'='*60}\n")

        # Load JSON files
        data = self.load_json_files(json_files)
        if not data:
            print("Failed to load JSON files", file=sys.stderr)
            return False

        # Normalize domain names
        data = self.normalize_domain_names(data)

        # Build object maps
        self.build_object_map(data)

        print(f"\n✓ Indexed {len(self.all_objects)} objects across {len(data)} domains")
        print(f"✓ Indexed {len(self.all_relationships)} relationships\n")

        # Generate individual domain ERDs
        print("Generating domain Mermaid diagrams...")
        domain_display_names = {
            "PCM": "PCM",
            "Pricing": "Pricing",
            "RateManagement": "RateManagement",
            "Configurator": "Configurator",
            "TransactionManagement": "TransactionManagement",
            "DRO": "DRO",
            "UsageManagement": "UsageManagement",
            "Billing": "Billing",
        }

        for domain, objects in self.domain_objects.items():
            display_name = domain_display_names.get(domain, domain)
            self.generate_domain_erd(domain, objects, display_name)

        # Generate master ERD
        print("\nGenerating master Mermaid diagram...")
        self.generate_master_erd(data)

        # Generate HTML viewer
        print("\nGenerating interactive HTML viewer...")
        self.generate_html_viewer(data)

        print(f"\n{'='*60}")
        print(f"✓ All ERDs generated successfully!")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"{'='*60}\n")

        return True


def main():
    """Main entry point."""
    # Find JSON files in the parent directory or specified paths
    base_dir = Path(__file__).parent.parent  # /mnt/rlm-base-dev

    json_files = [
        "/sessions/clever-intelligent-ramanujan/erd_pcm_pricing_rates.json",
        "/sessions/clever-intelligent-ramanujan/erd_txn_dro.json",
        "/sessions/clever-intelligent-ramanujan/erd_usage_billing.json",
    ]

    # Output directory
    output_dir = base_dir / "docs" / "erds"

    # Create builder and run
    builder = ERDBuilder(str(output_dir))
    success = builder.run(json_files)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
