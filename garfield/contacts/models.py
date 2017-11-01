from django.db import models

from phone_numbers.models import PhoneNumber


class Contact(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    whitepages_first_name = models.CharField(max_length=255,
                                             blank=True,
                                             null=True)
    whitepages_middle_name = models.CharField(max_length=255,
                                              blank=True,
                                              null=True)
    whitepages_last_name = models.CharField(max_length=255,
                                            blank=True,
                                            null=True)
    whitepages_gender = models.CharField(max_length=255,
                                         blank=True,
                                         null=True)
    whitepages_entity_type = models.CharField(max_length=255,
                                              blank=True,
                                              null=True)
    whitepages_business_name = models.CharField(max_length=255,
                                                blank=True,
                                                null=True)
    whitepages_address = models.CharField(max_length=255,
                                          blank=True,
                                          null=True)
    whitepages_address_two = models.CharField(max_length=255,
                                              blank=True,
                                              null=True)
    whitepages_city = models.CharField(max_length=255,
                                       blank=True,
                                       null=True)
    whitepages_state = models.CharField(max_length=255,
                                        blank=True,
                                        null=True)
    whitepages_country = models.CharField(max_length=255,
                                          blank=True,
                                          null=True)
    whitepages_zip_code = models.CharField(max_length=255,
                                           blank=True,
                                           null=True)
    whitepages_address_type = models.CharField(max_length=255,
                                               blank=True,
                                               null=True)
    whitepages_latitude = models.FloatField(null=True)
    whitepages_longitude = models.FloatField(null=True)
    whitepages_accuracy = models.CharField(max_length=255,
                                           blank=True,
                                           null=True)
    whitepages_prepaid = models.NullBooleanField(default=False)
    whitepages_phone_type = models.CharField(max_length=255,
                                             blank=True,
                                             null=True)
    whitepages_commercial = models.NullBooleanField(default=False)

    phone_number = models.CharField(max_length=255)
    carrier = models.CharField(max_length=255,
                               blank=True,
                               null=True)
    phone_number_type = models.CharField(max_length=255,
                                         blank=True,
                                         null=True)
    phone_number_friendly = models.CharField(max_length=255,
                                             blank=True,
                                             null=True)

    nextcaller_first_name = models.CharField(max_length=255,
                                             blank=True,
                                             null=True)
    nextcaller_middle_name = models.CharField(max_length=255,
                                              blank=True,
                                              null=True)
    nextcaller_last_name = models.CharField(max_length=255,
                                            blank=True,
                                            null=True)
    nextcaller_gender = models.CharField(max_length=255,
                                         blank=True,
                                         null=True)
    nextcaller_age = models.CharField(max_length=255,
                                      blank=True,
                                      null=True)
    nextcaller_marital_status = models.CharField(max_length=255,
                                                 blank=True,
                                                 null=True)
    nextcaller_children_presence = models.NullBooleanField(default=False)
    nextcaller_high_net_worth = models.NullBooleanField(default=False)
    nextcaller_home_owner_status = models.CharField(max_length=255,
                                                    blank=True,
                                                    null=True)
    nextcaller_household_income = models.CharField(max_length=255,
                                                   blank=True,
                                                   null=True)
    nextcaller_length_of_residence = models.CharField(max_length=255,
                                                      blank=True,
                                                      null=True)
    nextcaller_market_value = models.CharField(max_length=255,
                                               blank=True,
                                               null=True)
    nextcaller_education = models.CharField(max_length=255,
                                            blank=True,
                                            null=True)
    nextcaller_occupation = models.CharField(max_length=255,
                                             blank=True,
                                             null=True)
    nextcaller_address = models.CharField(max_length=255,
                                          blank=True,
                                          null=True)
    nextcaller_address_two = models.CharField(max_length=255,
                                              blank=True,
                                              null=True)
    nextcaller_city = models.CharField(max_length=255,
                                       blank=True,
                                       null=True)
    nextcaller_state = models.CharField(max_length=255,
                                        blank=True,
                                        null=True)
    nextcaller_country = models.CharField(max_length=255,
                                          blank=True,
                                          null=True)
    nextcaller_zip_code = models.CharField(max_length=255,
                                           blank=True,
                                           null=True)
    nextcaller_prepaid = models.NullBooleanField(default=False)
    nextcaller_carrier = models.CharField(max_length=255,
                                          blank=True,
                                          null=True)
    nextcaller_phone_type = models.CharField(max_length=255,
                                             blank=True,
                                             null=True)
    nextcaller_identity_type = models.CharField(max_length=255,
                                                blank=True,
                                                null=True)
    nextcaller_business_name = models.CharField(max_length=255,
                                                blank=True,
                                                null=True)
    nextcaller_email = models.EmailField(blank=True, null=True)
    nextcaller_twitter = models.CharField(max_length=255,
                                          blank=True,
                                          null=True)
    nextcaller_facebook = models.CharField(max_length=255,
                                           blank=True,
                                           null=True)
    nextcaller_linkedin = models.CharField(max_length=255,
                                           blank=True,
                                           null=True)

    ter_username = models.CharField(max_length=255,
                                    blank=True,
                                    null=True)

    photo = models.ImageField(upload_to="contact_photos/",
                              blank=True)

    identified = models.BooleanField(default=False)
    registed_offender = models.BooleanField(default=False)
    arrested = models.BooleanField(default=False)
    deterred = models.BooleanField(default=False)
    do_not_deter = models.BooleanField(default=False)
    deterrents_received = models.IntegerField(default=0)

    related_phone_numbers = models.ManyToManyField(PhoneNumber)

    def __str__(self):
        return "{0}: {1} {2}".format(self.phone_number,
                                     self.nextcaller_first_name,
                                     self.nextcaller_last_name)
