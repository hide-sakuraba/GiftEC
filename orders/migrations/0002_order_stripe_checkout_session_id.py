from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_checkout_session_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Stripe Checkout Session ID'),
        ),
    ]
