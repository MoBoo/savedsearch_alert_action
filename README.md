# Splunk Saved Searches Alert Action
Custom Splunk Alert Action to run saved search whenever the specified alert is triggered.

Inspired by and developed for [this reddit post](https://www.reddit.com/r/Splunk/comments/km14pj/alert_action_to_fire_off_other_searchesreports/).

Due to limited capabilities of the custom [<splunk-search-dropdown>](https://docs.splunk.com/Documentation/Splunk/8.1.1/AdvancedDev/CustomAlertUI#Custom_HTML_elements)-tag provided by Splunk, only a single saved-search can be run from an alert (selecting multiple isn't supported). Also only a single alert action can be defined, which eliminates this workaround-idea.

## Workaround by specifing a string and a seperator.
A second Custom Alert Action is implemented, which uses a textarea-input as well as a seperator (comma or newline) to split the input string.

# Usage
Create Alert and choose either 'Saved Search Alert Action' or 'Saved Search Alert Action by List' and fill in all the inputs.
<TODO> Add Tutorial and Images
