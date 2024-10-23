Command = {
    "type": "flex",
    "altText": "Admin Command list",
    "contents": {
        "type": "bubble",
        "styles":{"header": {"backgroundColor": "#f5cba7"}},
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [{"type": "text", "weight": "bold", "align": "center", "text": "Admin Command Center"}]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "Save Chat history",
                        "text": "/admin save_memory"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "Reset Cache",
                        "text": "/admin reset_cache"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "Update Database",
                        "text": "/admin force_updb"
                    }
                },
                {
                    "type": "text",
                    "wrap": True,
                    "text": "To change database url:\nType /admin update_link ->[link]"
                }
            ]
        }
    },
}