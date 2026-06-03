from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .choices import price_choices, bedroom_choices, state_choices
from .models import Listing, Favourite


def index(request):
    listings = Listing.objects.order_by('-list_date').filter(is_published=True)
    paginator = Paginator(listings, 6)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)
    return render(request, 'listings/listings.html', {'listings': paged_listings})


def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    is_favourite = False
    if request.user.is_authenticated:
        is_favourite = Favourite.objects.filter(user=request.user, listing=listing).exists()
    return render(request, 'listings/listing.html', {
        'listing': listing,
        'is_favourite': is_favourite,
    })


def search(request):
    queryset_list = Listing.objects.filter(is_published=True).order_by('-list_date')

    if request.GET.get('keywords'):
        queryset_list = queryset_list.filter(description__icontains=request.GET['keywords'])

    if request.GET.get('city'):
        queryset_list = queryset_list.filter(city__iexact=request.GET['city'])

    if request.GET.get('state'):
        queryset_list = queryset_list.filter(state__iexact=request.GET['state'])

    if request.GET.get('bedrooms'):
        queryset_list = queryset_list.filter(bedrooms__lte=request.GET['bedrooms'])

    if request.GET.get('price'):
        price_range = request.GET['price'].split('-')
        if len(price_range) == 2:
            queryset_list = queryset_list.filter(
                price__gte=price_range[0],
                price__lte=price_range[1]
            )

    paginator = Paginator(queryset_list, 6)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)

    context = {
        'state_choices': state_choices,
        'bedroom_choices': bedroom_choices,
        'price_choices': price_choices,
        'listings': paged_listings,
        'values': request.GET,
    }
    return render(request, 'listings/search.html', context)


@login_required
def toggle_favourite(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    fav, created = Favourite.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        fav.delete()
        messages.info(request, f'"{listing.title}" removed from your favourites.')
    else:
        messages.success(request, f'"{listing.title}" added to your favourites.')
    return redirect('listing', listing_id=listing_id)