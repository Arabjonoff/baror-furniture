import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


# Eski choices qiymatlarini yangi jadval nomlariga moslash
MATERIAL_MAP = {
    'yogoch': "Yog'och",
    'ldsp': 'LDSP',
    'metall': 'Metall',
    'mato': 'Mato',
    'teri': 'Teri',
}
ROOM_TYPE_MAP = {
    'mehmonxona': 'Mehmonxona',
    'yotoqxona': 'Yotoqxona',
    'oshxona': 'Oshxona',
    'ofis': 'Ofis',
    'bolalar_xonasi': 'Bolalar xonasi',
}


def forwards(apps, schema_editor):
    Product = apps.get_model('catalog', 'Product')
    Material = apps.get_model('catalog', 'Material')
    RoomType = apps.get_model('catalog', 'RoomType')

    # Ishlatilayotgan eski qiymatlarni yangi yozuvlarga aylantiramiz
    material_cache = {}
    for code, name in MATERIAL_MAP.items():
        obj, _ = Material.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
        material_cache[code] = obj

    room_cache = {}
    for code, name in ROOM_TYPE_MAP.items():
        obj, _ = RoomType.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
        room_cache[code] = obj

    for product in Product.objects.all():
        code = product.material_code
        if code and code in material_cache:
            product.material = material_cache[code]
        room_code = product.room_type_code
        if room_code and room_code in room_cache:
            product.room_type = room_cache[room_code]
        product.save(update_fields=['material', 'room_type'])


def backwards(apps, schema_editor):
    Product = apps.get_model('catalog', 'Product')
    name_to_material_code = {v: k for k, v in MATERIAL_MAP.items()}
    name_to_room_code = {v: k for k, v in ROOM_TYPE_MAP.items()}
    for product in Product.objects.all():
        product.material_code = name_to_material_code.get(
            product.material.name if product.material else '', ''
        )
        product.room_type_code = name_to_room_code.get(
            product.room_type.name if product.room_type else '', ''
        )
        product.save(update_fields=['material_code', 'room_type_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_banner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='nomi')),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Material',
                'verbose_name_plural': 'Materiallar',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='nomi')),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Xona turi',
                'verbose_name_plural': 'Xona turlari',
                'ordering': ['name'],
            },
        ),
        # Eski char qiymatlarni vaqtincha saqlab turamiz
        migrations.RenameField(model_name='product', old_name='material', new_name='material_code'),
        migrations.RenameField(model_name='product', old_name='room_type', new_name='room_type_code'),
        # Yangi FK maydonlar
        migrations.AddField(
            model_name='product',
            name='material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='catalog.material', verbose_name='material'),
        ),
        migrations.AddField(
            model_name='product',
            name='room_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='catalog.roomtype', verbose_name='xona turi'),
        ),
        migrations.RunPython(forwards, backwards),
        # Eski maydonlarni olib tashlaymiz
        migrations.RemoveField(model_name='product', name='material_code'),
        migrations.RemoveField(model_name='product', name='room_type_code'),
    ]
