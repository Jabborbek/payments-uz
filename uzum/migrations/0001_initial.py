from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='UzumTransactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_id', models.CharField(max_length=255, unique=True, db_index=True)),
                ('order_id', models.CharField(max_length=256)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('state', models.IntegerField(choices=[
                    (0, 'Pending'),
                    (1, 'Paid'),
                    (-1, 'Canceled'),
                ], default=0)),
                ('cancel_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('performed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Uzum Transaction',
                'verbose_name_plural': 'Uzum Transactions',
                'db_table': 'uzum_transactions',
                'ordering': ['-created_at'],
            },
        ),
    ]
