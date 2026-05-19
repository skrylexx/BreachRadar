import os

file_path = '/ransomlook/website/web/api/genericapi.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

# Find where to insert new routes (after the Namespace definition)
insert_idx = -1
for i, line in enumerate(lines):
    if "api = Namespace('GenericAPI'" in line:
        insert_idx = i + 1
        break

if insert_idx != -1:
    new_routes = [
        "\n",
        "@api.route('/victim')\n",
        "@api.doc(description='Search for a victim name', tags=['generic'])\n",
        "class VictimSearch(Resource):\n",
        "    def get(self):\n",
        "        name = request.args.get('name', '').lower()\n",
        "        if not name:\n",
        "            return []\n",
        "        posts = []\n",
        "        red = Redis(host='ransomlook-redis', port=6379, db=2)\n",
        "        for key in red.keys():\n",
        "            try:\n",
        "                entries = json.loads(red.get(key))\n",
        "                for entry in entries:\n",
        "                    if name in entry['post_title'].lower() or (entry.get('description') and name in entry['description'].lower()):\n",
        "                        entry['group_name'] = key.decode()\n",
        "                        posts.append(entry)\n",
        "            except: continue\n",
        "        return posts\n",
        "\n",
        "@api.route('/stats')\n",
        "class StatsV1(Resource):\n",
        "    def get(self):\n",
        "        red_groups = Redis(host='ransomlook-redis', port=6379, db=0)\n",
        "        red_posts = Redis(host='ransomlook-redis', port=6379, db=2)\n",
        "        total_posts = 0\n",
        "        for k in red_posts.keys():\n",
        "            try: total_posts += len(json.loads(red_posts.get(k)))\n",
        "            except: continue\n",
        "        return {\n",
        "            'groups': len(red_groups.keys()),\n",
        "            'posts': total_posts,\n",
        "            'last_update': datetime.now().isoformat()\n",
        "        }\n",
        "\n",
        "@api.route('/key')\n",
        "@api.doc(description='Get the auto-generated API key (internal only)', tags=['generic'])\n",
        "class GetLocalKey(Resource):\n",
        "    def get(self):\n",
        "        from website.web.helpers import build_keys_table\n",
        "        keys = build_keys_table()\n",
        "        if keys:\n",
        "            return {'api_key': list(keys.keys())[0]}\n",
        "        return {'api_key': None}\n"
    ]
    
    # Check if already patched
    if "@api.route('/victim')" not in "".join(lines):
        for line in reversed(new_routes):
            lines.insert(insert_idx, line)
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
        print("Successfully added /api/victim and /api/stats to genericapi.py")
    else:
        print("genericapi.py already patched")
else:
    print("Could not find insertion point in genericapi.py")
