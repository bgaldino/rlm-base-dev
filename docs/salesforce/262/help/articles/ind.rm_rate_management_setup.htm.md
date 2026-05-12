---
article_id: ind.rm_rate_management_setup.htm
title: Rate Management Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rate_management_setup.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Rate Management Setup

Rate Management provides the key tools to manage rates for consumption-based products. To leverage these tools effectively, you must first complete the setup detailed in this section. This process represents our recommended base configuration and is a prerequisite for building any custom solution. It ensures essential procedures can be customized and data can be synchronized for accuracy. Complete all of the following steps before continuing to design your rating solution.

Enable Rate Management
Give your users access to the Rate Management objects and features.
Enable Rating Waterfall
Rating Waterfall provides insights and reasons for every step of the rating process. Let's say that while calculating the final net rate of a usage resource, you find out that the discount is less than anticipated. With Waterfall View, you can view the rate breakups at every step along with the reason for the addition or deduction.
Enable Rating Waterfall Persistence
Waterfall persistence stores the rating logs in a structured manner within the Salesforce database. Rating waterfall logs capture the sequence of rating decisions applied during execution for efficient tracking and retrieval of rating information.
Create Price Book Rate Cards
To determine the rates for a usage resource, map the price book related to the sellable product with a rate card that’s related to the corresponding usage resource. Create a Price Book Rate Card record for each rate card type, such as Base or Tier.
Rate Cards and Rate Card Entries
Define the rules that are used to rate the consumption of a group of usage resources within a product. If the customer consumes the usage resource beyond the granted limits or period, specific rates are applied.
Create a Rating Procedure by Cloning the Expression Set Template
Clone a predefined rating procedure template, such as the Default Rating Procedure and the Negotiable Rating Procedure, available with Rate Management. You can also build a custom rating procedure to meet your business’s unique needs.
Simulate and Activate Your Rating Procedure
Before you activate your rating procedure, run simulations to test if the variables that you entered are accurate. If your rating procedure doesn’t work as expected, edit the values that you entered and try again. When you’re satisfied, activate the rating procedure version.
Select Rating Discovery Procedure
To select a rating discovery procedure, you must first clone the predefined rating discovery procedure available with Salesforce Rate Management. You can also build a custom rating procedure to meet the unique needs of your business.
Record Sharing for Rate Management
For runtime users to access the data created by rating designers, managers or catalog admins, set up record sharing for all the Rate Management entities.
