from __future__ import absolute_import

from rest_framework.response import Response
from sentry import features
from sentry.models import DiscoverSavedQuery
from sentry.api.serializers import serialize
from sentry.api.bases.organization import OrganizationPermission
from sentry.api.bases.discoversavedquery import DiscoverSavedQuerySerializer
from sentry.api.bases import OrganizationEndpoint


class OrganizationDiscoverSavedQueriesEndpoint(OrganizationEndpoint):
    permission_classes = (OrganizationPermission, )

    def get(self, request, organization):
        """
        List saved queries for organization
        """
        if not features.has('organizations:discover', organization, actor=request.user):
            return self.respond(status=404)

        saved_queries = list(DiscoverSavedQuery.objects.filter(
            organization=organization,
        ).all().prefetch_related('projects').order_by('name'))

        return Response(serialize(saved_queries), status=200)

    def post(self, request, organization):
        """
        Create a saved query
        """
        if not features.has('organizations:discover', organization, actor=request.user):
            return self.respond(status=404)

        serializer = DiscoverSavedQuerySerializer(data=request.DATA)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.object

        model = DiscoverSavedQuery.objects.create(
            organization=organization,
            name=data['name'],
            query=data['query'],
        )

        model.set_projects(data['project_ids'])

        return Response(serialize(model), status=201)
