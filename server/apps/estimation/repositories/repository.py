from ..models import Project, ProjectResources, ProjectLabour
from django.shortcuts import get_object_or_404


class ProjectRepository:
    @staticmethod
    def get_all():
        return Project.objects.all()

    @staticmethod
    def get_by_id(pk):
        return Project.objects.filter(id=pk).first()

    @staticmethod
    def create(validated_data):
        return Project.objects.create(**validated_data)

    @staticmethod
    def update(pk, validated_data):
        Project.objects.filter(id=pk).update(**validated_data)
        return Project.objects.get(id=pk)

    @staticmethod
    def delete(pk):
        deleted, _ = Project.objects.filter(id=pk).delete()
        return deleted


class ProjectResourcesRepository:
    @staticmethod
    def get_all_by_project(project_id):
        return ProjectResources.objects.filter(project_id=project_id)

    @staticmethod
    def get_by_id(project_id, pk):
        return ProjectResources.objects.filter(project_id=project_id, id=pk).first()

    @staticmethod
    def create(project_id, validated_data):
        validated_data['project_id'] = project_id
        return ProjectResources.objects.create(**validated_data)

    @staticmethod
    def update(project_id, pk, validated_data):
        ProjectResources.objects.filter(project_id=project_id, id=pk).update(**validated_data)
        return ProjectResources.objects.get(id=pk)

    @staticmethod
    def delete(project_id, pk):
        deleted, _ = ProjectResources.objects.filter(project_id=project_id, id=pk).delete()
        return deleted


class ProjectLabourRepository:
    @staticmethod
    def get_all_by_project(project_id):
        return ProjectLabour.objects.filter(project_id=project_id)

    @staticmethod
    def get_by_id(project_id, pk):
        return ProjectLabour.objects.filter(project_id=project_id, id=pk).first()

    @staticmethod
    def create(project_id, validated_data):
        validated_data['project_id'] = project_id
        return ProjectLabour.objects.create(**validated_data)

    @staticmethod
    def update(project_id, pk, validated_data):
        ProjectLabour.objects.filter(project_id=project_id, id=pk).update(**validated_data)
        return ProjectLabour.objects.get(id=pk)

    @staticmethod
    def delete(project_id, pk):
        deleted, _ = ProjectLabour.objects.filter(project_id=project_id, id=pk).delete()
        return deleted
