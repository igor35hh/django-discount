# django-discount
django discount app
there are implemented discounts for product, brand, category and customer
queryset of product has discounts of every related model
queryset of customer has discounts of every related model
it is useful for using in admin and view as well
for computing discounts here were used raw query with further union queryset of main model, window functions for optimisation query.
it tested for sqlite3, for psql it is necessary to use function greatest(,,,) instead of max(,,,)
