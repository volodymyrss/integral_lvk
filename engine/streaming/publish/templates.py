from jinja2 import Template

title_template = Template("""
INTEGRAL follow-up of {{parse.event_id}}
""")

body_template = Template("""
INTEGRAL follow-up of {{parse.event_id}} at {{parse.t0_utc}}

{% if integralallsky %}
SPI-ACS excesses:
{%- for entry in integralallsky.reportable_excesses -%}
{%- if entry.excess.FAP < 1 %}
at T0+{{entry.excess.rel_s_scale | round(2)}} FAP = {{entry.excess.FAP | round(3)}}
{%- endif -%}
{%- endfor -%}
{% endif %}

{% if ivis %}
{% endif %}

{{ rtstate['prophecy'][0] }}

""")


def format(data, test=True):
    title = title_template.render(data)
    body = body_template.render(data)

    print(title)
    print(body)

    try:
        gcn_circular_text = data['gcn']['gcn_wrapped_text']
    except KeyError:
        gcn_circular_text = ''

    return dict(
        title=title,
        body=body,
        gcn_circular_text=gcn_circular_text,
    )
