from pytest_django.asserts import assertRedirects

from django.urls import reverse

import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from notes.forms import WARNING

from notes.models import Note

from pytils.translit import slugify


def test_user_can_create_note(author_client, author, form_data):
    url = reverse('notes:add')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    url = reverse('notes:add')
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Note.objects.count() == 0


def test_not_unique_slug(author_client, note, form_data):
    url = reverse('notes:add')
    form_data['slug'] = note.slug
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
    assert Note.objects.count() == 1


def test_empty_slug(author_client, form_data):
    url = reverse('notes:add')
    form_data.pop('slug')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    expected_slug = slugify(form_data['title'])
    assert new_note.slug == expected_slug


def test_author_can_edit_note(author_client, form_data, note):
    url = reverse('notes:edit', args=(note.slug,))
    response = author_client.post(url, form_data)
    assertRedirects(response, reverse('notes:success'))
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']


def test_other_user_cant_delete_note(not_author_client,
                                     slug_for_args):
    url = reverse('notes:delete', args=slug_for_args)
    note_count_before = Note.objects.count()
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == note_count_before


def test_other_user_cant_delete_note(not_author_client,
                                     slug_for_args):
    url = reverse('notes:delete', args=slug_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1
