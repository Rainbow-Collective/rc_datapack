import errno
import json
import os


def get_file_list(entry):
    files = list()
    for (dir_path, dir_names, filenames) in os.walk(entry):
        files += [os.path.join(dir_path, file) for file in filenames if not file.endswith('.gitkeep')]
    return files


def safe_path_create(path):
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


input_path = os.path.join('.', 'input')
output_path = os.path.join('.', 'output')

recipe_paths = get_file_list(input_path)

for recipe_path in recipe_paths:
    relative_path = os.path.relpath(recipe_path, input_path)
    file_out = os.path.join(output_path, relative_path)
    print(relative_path)
    with(open(recipe_path, 'r')) as rf:
        data = json.load(rf)
        items = list()
        if data['type'] == 'crafting_shaped':
            items = [key['item'] for key in data['key'].values()]
        elif data['type'] == 'crafting_shapeless':
            items = [ingredient['item'] for ingredient in data['ingredients']]
        else:
            print('recipe type not handled')

        items = list(set(items))
        advancement = dict(
            parent="minecraft:recipes/root",
            criteria=dict(
                has_items=dict(
                    trigger='minecraft:inventory_changed',
                    conditions=dict(
                        items=list(
                            [dict(item=item_name) for item_name in items]
                        )
                    )
                ),
                has_the_recipe=dict(
                    trigger='minecraft:recipe_unlocked',
                    conditions=dict(
                        recipe='{}:{}'.format(data['group'], relative_path.replace('\\', '/'))
                    )
                )
            ),
            requirements=[['has_items', 'has_the_recipe']],
            rewards=dict(
                recipes=list(['{}:{}'.format(data['group'], relative_path.replace('\\', '/'))])
            )
        )

        safe_path_create(file_out)
        with(open(file_out, 'w+')) as wf:
            json.dump(advancement, wf, indent=4)
