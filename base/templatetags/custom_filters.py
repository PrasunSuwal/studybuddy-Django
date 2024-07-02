from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def display_message(context, message_tag):
    messages = context["messages"]
    for message in messages:
        if message_tag in message.tags:
            return str(message)