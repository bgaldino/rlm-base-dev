---
article_id: ind.product_configurator_flow_screen_components.htm
title: Product Configurator Flow Screen Components
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_flow_screen_components.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Product Configurator Flow Screen Components

Product Configurator provides a sample flow, Default Product Configurator Flow. The default flow contains a screen element with components that collect and display information in Product Configurator. For information on each screen component, including its responsibilities and properties, see the topics linked here.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Breadcrumbs
Breadcrumbs shows the navigation path through the product bundle hierarchy in Product Configurator. The component displays clickable breadcrumb links so users can move between levels, such as root product → option group → option. Breadcrumbs has no output properties and doesn’t listen to any events.
Data Manager
Data Manager is the state management and orchestration component for Product Configurator. This component stores product data and uses flow events to propagate the data to other components on the flow screen.
Footer
Footer is the action bar at the bottom of Product Configurator. The component shows validation messages and action buttons. Footer publishes Lightning Message Service (LMS) events to Data Manager when users click these actions. Button visibility depends on context, such as nested product, preview mode, instant pricing, validation, and so on. Footer has no output properties and doesn’t listen to any events.
Header
Header, also called Config Header, is a control panel component that displays the configuration header with toggles, tabs, and informational banners at the top of Product Configurator. The component provides controls for users to toggle instant pricing, validation, and layout modes, and to navigate between multiple root products via tabs. Header has no output properties, and doesn’t listen to any events.
Messages
Messages is a UI display component that renders validation messages to Product Configurator users. The component shows messages in an expandable accordion and filters messages by severity, either Error, Warning, or Info. Messages has no output properties, and doesn’t listen to or fire any events.
Option Groups
Option Groups is the container component that shows child products organized into groups. The component manages option selection, dynamic option addition, cloning, and search navigation. Option Groups has no output properties.
Product Attributes
Product Attributes is the container component that shows product attributes in Product Configurator. The component organizes attributes by category and supports multiple display modes, including tabs, sections, and accordions. Product Attributes has no output properties and doesn’t listen to any events.
Product Header
Product Header shows product information at the top of each product or option in Product Configurator. The component shows product name, description, image, quantity input, pricing, and Product Selling Model (PSM) selection. It's a UI presentation component that publishes user changes via Lightning Message Service (LMS) events. Product Header has no output properties.
Summary
Summary is a UI display component that renders the pricing summary section in Product Configurator. The component displays the current product's pricing information, including one-time, monthly, and annual totals, along with a hierarchical breakdown of child products and their prices. Summary has no output properties, and doesn’t listen to or fire any events.
Transaction Header
Transaction Header is a navigation and control component that displays a header with a dynamic Back or Cancel button at the top of Product Configurator. The component allows users to exit the configurator and navigate back to the parent transaction record. Transaction Header has no output properties and doesn’t listen to any events.
