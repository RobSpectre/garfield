from django.db import models


class John(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    whitepages_first_name = models.CharField(max_length=255, blank=True)
    whitepages_middle_name = models.CharField(max_length=255, blank=True)
    whitepages_last_name = models.CharField(max_length=255, blank=True)
    whitepages_gender = models.CharField(max_length=255, blank=True)
    whitepages_address = models.CharField(max_length=255, blank=True)
    whitepages_address_two = models.CharField(max_length=255, blank=True)
    whitepages_city = models.CharField(max_length=255, blank=True)
    whitepages_state = models.CharField(max_length=255, blank=True)
    whitepages_country = models.CharField(max_length=255, blank=True)
    whitepages_zip_code = models.CharField(max_length=255, blank=True)
    whitepages_address_type = models.CharField(max_length=255, blank=True)
    whitepages_latitude = models.FloatField(blank=True)
    whitepages_longitude = models.FloatField(blank=True)
    whitepages_accuracy = models.CharField(max_length=255, blank=True)
    whitepages_prepaid = models.BooleanField(blank=True)
    whitepages_phone_type = models.BooleanField(blank=True)
    whitepages_identity_type = models.CharField(max_length=255,
                                                blank=True)
    whitepages_business_name = models.CharField(max_length=255,
                                                blank=True)

    phone_number = models.CharField(max_length=255, blank=True)
    carrier = models.CharField(max_length=255, blank=True)
    phone_number_type = models.CharField(max_length=255, blank=True)
    phone_number_friendly = models.CharField(max_length=255, blank=True)

    nextcaller_first_name = models.CharField(max_length=255, blank=True)
    nextcaller_middle_name = models.CharField(max_length=255, blank=True)
    nextcaller_last_name = models.CharField(max_length=255, blank=True)
    nextcaller_gender = models.CharField(max_length=255, blank=True)
    nextcaller_age = models.CharField(max_length=255, blank=True)
    nextcaller_marital_status = models.BooleanField(blank=True)
    nextcaller_children_presence = models.BooleanField(blank=True)
    nextcaller_address = models.CharField(max_length=255, blank=True)
    nextcaller_address_two = models.CharField(max_length=255, blank=True)
    nextcaller_city = models.CharField(max_length=255, blank=True)
    nextcaller_state = models.CharField(max_length=255, blank=True)
    nextcaller_country = models.CharField(max_length=255, blank=True)
    nextcaller_zip_code = models.CharField(max_length=255, blank=True)
    nextcaller_address_type = models.CharField(max_length=255, blank=True)
    nextcaller_latitude = models.FloatField(blank=True)
    nextcaller_longitude = models.FloatField(blank=True)
    nextcaller_accuracy = models.CharField(max_length=255, blank=True)
    nextcaller_prepaid = models.BooleanField(blank=True)
    nextcaller_phone_type = models.BooleanField(blank=True)
    nextcaller_identity_type = models.CharField(max_length=255,
                                                blank=True)
    nextcaller_business_name = models.CharField(max_length=255,
                                                blank=True)
    nextcaller_email = models.EmailField(blank=True)
    nextcaller_twitter = models.CharField(max_length=255, blank=True)
    nextcaller_facebook = models.CharField(max_length=255, blank=True)
    nextcaller_linkedin = models.CharField(max_length=255, blank=True)

    ter_username = models.CharField(max_length=255)

    photo = models.ImageField(upload_to="john_photos/",
                              blank=True)
