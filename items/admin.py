from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import Item, ClaimRequest, Notification


class MissingItemsFilter(SimpleListFilter):
    title = 'Missing items'
    parameter_name = 'missing_items'

    def lookups(self, request, model_admin):
        return (('yes', 'Show missing items'),)

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(report_type='Lost')
        return queryset


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'report_type',
        'is_missing_item',
        'category',
        'location',
        'status',
        'reported_by',
        'created_at',
    )

    list_filter = (MissingItemsFilter, 'report_type', 'category', 'status')
    search_fields = ('title', 'description', 'location')
    ordering = ('-created_at',)

    @admin.display(boolean=True, description='Missing item')
    def is_missing_item(self, obj):
        return obj.report_type == 'Lost'

    def save_model(self, request, obj, form, change):
        old_status = None

        if change:
            old_status = Item.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if old_status != obj.status:
            if obj.status == 'Approved':
                Notification.objects.create(
                    recipient=obj.reported_by,
                    message=f'Your {obj.report_type.lower()} report "{obj.title}" has been approved.'
                )

            elif obj.status == 'Rejected':
                Notification.objects.create(
                    recipient=obj.reported_by,
                    message=f'Your {obj.report_type.lower()} report "{obj.title}" has been rejected.'
                )


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'claimant',
        'status',
        'created_at',
    )

    list_filter = ('status',)
    search_fields = ('item__title', 'claimant__username', 'message')
    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

    fields = (
        'item',
        'claimant',
        'message',
        'status',
        'created_at',
    )

    def save_model(self, request, obj, form, change):
        old_status = None

        if change:
            old_status = ClaimRequest.objects.get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if old_status != obj.status:
            if obj.status == 'Approved':
                obj.item.status = 'Returned'
                obj.item.save(update_fields=['status'])

                Notification.objects.create(
                    recipient=obj.claimant,
                    message=f'Your claim for "{obj.item.title}" has been approved!'
                )

            elif obj.status == 'Rejected':
                Notification.objects.create(
                    recipient=obj.claimant,
                    message=f'Your claim for "{obj.item.title}" has been rejected.'
                )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient',
        'message',
        'is_read',
        'created_at',
    )

    list_filter = ('is_read',)
    search_fields = ('recipient__username', 'message')
    ordering = ('-created_at',)
