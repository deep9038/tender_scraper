{% macro wb_date(field_name) %}

    safe_ts(nullif(raw->>'{{ field_name }}', 'NA'), 'DD-Mon-YYYY HH12:MI AM')

{% endmacro %}
