# Get PagerDuty Account info

This script will output four CSV files with data on a PagerDuty account's users, escalation policies, schedules, and teams.

## Usage

1. Replace the `ACCESS_TOKEN` variable on line 32 with a v2 read-only PagerDuty access token

2. Execute the `get_info.py` script

## CSV files exported

1. User data `user_data_<timestamp>.csv`:

    **id**: The ID of the user

    **name**: The name of the user

    **email**: The email address of the user

    **role**: The role of the user

    **contact_method_id**: The ID of the contact method

    **contact_method_type**: The type of contact method

    **contact_method_label**: The label for the contact method

    **contact_method_address**: The address of the contact method

2. Escalation policy data `escalation_policy_data_<timestamp>.csv`:

    **id**: The ID of the escalation policy

    **name**: The name of the escalation policy

    **escalation_rule_id**: The ID of the escalation rule

    **escalation_rule_delay**: The delay in minutes for the escalation rule

    **escalation_rule_target_id**: The ID of the escalation rule target

    **escalation_rule_target_type**: The type of the escalation rule target

    **escalation_rule_target_name**: The name of the escalation rule target

3. Schedule data `schedule_data_<timestamp>.csv`:

    **id**: The ID of the schedule

    **name**: The name of the schedule

    **description**: The description of the schedule

    **time_zone**: The time zone of the schedule

    **oncall_id**: The ID of the on-call user

    **oncall_name**: The name of the on-call user

    **oncall_escalation_level**: The escalation level of the on-call user

    **oncall_shift_start**: The start time for the on-call user's shift

    **oncall_shift_end**: The end time for the on-call user's shift

4. Team data `team_data_<timestamp>.csv`:

    **id**: The ID of the team

    **name**: The name of the team

    **user_id**: The ID of the user on the team

    **user_name**: The name of the user on the team

    **schedule_id**: The ID of the schedule on the team

    **schedule_name**: The name of the schedule on the team

    **escalation_policy_id**: The ID of the escalation policy on the team

    **escalation_policy_name**: The name of the escalation policy on the team

    **service_id**: The ID of the service on the team

    **service_name**: The name of the service on the team

## Author

Luke Epp <lucas@pagerduty.com>
