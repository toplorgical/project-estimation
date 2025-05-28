from rest_framework import serializers
from ..models import Project, ProjectResources, ProjectLabour


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "report_name",
            "project_type",
            "project_location",
         
        ]

    def validate(self, data):
        if len(data.get("report_name", "")) < 3:
            raise serializers.ValidationError({"report name": "Report name must be at least 3 characters long."})
        if len(data.get("project_type", "")) < 3:
            raise serializers.ValidationError({"project type": "project type must be at least 3 characters long."})
        if len(data.get("project_location", "")) < 3:
            raise serializers.ValidationError({"project location": "project location must be at least 3 characters long."})
        return data


class ProjectResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectResources
        fields = [
            "id",
            "resource_type",
            "resource_name",
            "quantity",
            "unit_cost",
            "created_at",
            "updated_at"
        ]

    def validate_quantity(self, value):
        if not value.isdigit() or int(value) <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value

    def validate_unit_cost(self, value):
        try:
            cost = float(value)
            if cost <= 0:
                raise serializers.ValidationError("Unit cost must be greater than 0.")
        except ValueError:
            raise serializers.ValidationError("Unit cost must be a valid number.")
        return value


class ProjectLabourSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectLabour
        fields = [
            "id",
       
            "number_of_skills_worker",
            "number_of_unskills_worker",
            "project_duration",
            "project_size",
            "created_at",
            "updated_at"
        ]

    def validate_number_of_skills_worker(self, value):
        if not value.isdigit() or int(value) < 0:
            raise serializers.ValidationError("Number of skilled workers must be a non-negative integer.")
        return value

    def validate_number_of_unskills_worker(self, value):
        if not value.isdigit() or int(value) < 0:
            raise serializers.ValidationError("Number of unskilled workers must be a non-negative integer.")
        return value

    def validate(self, data):
        if not data["project_duration"].isdigit():
            raise serializers.ValidationError({"project_duration": "Duration must be numeric (in days or similar unit)."})
        if not data["project_size"]:
            raise serializers.ValidationError({"project_size": "Project size is required."})
        return data
