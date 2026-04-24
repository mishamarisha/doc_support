from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.core.paginator import Paginator

from .models import ImportedChange


def index(request):
    if request.method == 'POST':
        try:
            call_command('import_changelog', source='both')
            context = {
                'message': 'Changelog успешно импортирован',
                }
        except Exception as e:
            context = {
                'message': f'Ошибка: {e}',
            }
        return render(request, 'support/index.html', context)
    else:
        username = request.user
        context = {
            'username': username,
        }
        return render(request, 'support/index.html', context)


@login_required
def imported_changes_list(request):
    if request.method == 'POST' and 'import_changes' in request.POST:
        try:
            call_command('import_changelog', source='both')
            messages.success(request, 'Чейнджлог успешно импортирован')
        except Exception as e:
            messages.error(request, f'Ошибка импорта: {e}')
        return redirect('imported_changes_list')
    source_filter = request.GET.get('source', '')
    search_query = request.GET.get('q', '').strip()

    queryset = ImportedChange.objects.all()

    if source_filter in ['prod', 'dev']:
        queryset = queryset.filter(source=source_filter)
    if search_query:
        queryset = queryset.filter(text__icontains=search_query)

    # Сортировка
    order_by = request.GET.get('order_by', '-date')
    if order_by in ['date', '-date', 'source', '-source', 'imported_at', '-imported_at']:
        queryset = queryset.order_by(order_by)

    # Пагинация
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'source_filter': source_filter,
        'search_query': search_query,
        'current_order': order_by,
    }
    return render(request, 'support/imported_changes_list.html', context)
