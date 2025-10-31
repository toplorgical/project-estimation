from rest_framework import serializers
from .models import ExportJob


class ExportJobSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = ExportJob
        fields = [
            'id', 'export_type', 'status', 'project', 'estimate',
            'options', 'file_name', 'file_size', 'error_message',
            'progress', 'is_expired', 'created_at', 'started_at',
            'completed_at', 'expires_at'
        ]
        read_only_fields = (
            'id', 'status', 'file_name', 'file_size', 'error_message',
            'progress', 'created_at', 'started_at', 'completed_at', 'expires_at'
        )


class ExportRequestSerializer(serializers.Serializer):
    """Serializer for export requests"""
    export_type = serializers.ChoiceField(choices=ExportJob.EXPORT_TYPES)
    project_id = serializers.IntegerField(required=False)
    estimate_id = serializers.IntegerField(required=False)
    options = serializers.JSONField(required=False, default=dict)
    
    def validate(self, data):
        export_type = data['export_type']
        
        # Validate required fields based on export type
        if export_type in ['project_pdf', 'project_summary']:
            if not data.get('project_id'):
                raise serializers.ValidationError("project_id is required for project exports")
        
        elif export_type in ['estimate_pdf', 'estimate_excel']:
            if not data.get('estimate_id'):
                raise serializers.ValidationError("estimate_id is required for estimate exports")
        
        return data


class PDFExportOptionsSerializer(serializers.Serializer):
    """Options for PDF exports"""
    include_cover_page = serializers.BooleanField(default=True)
    include_summary = serializers.BooleanField(default=True)
    include_materials = serializers.BooleanField(default=True)
    include_machinery = serializers.BooleanField(default=True)
    include_labor = serializers.BooleanField(default=True)
    include_charts = serializers.BooleanField(default=True)
    include_substitutions = serializers.BooleanField(default=False)
    company_logo = serializers.URLField(required=False)
    custom_header = serializers.CharField(max_length=200, required=False)
    custom_footer = serializers.CharField(max_length=200, required=False)


class ExcelExportOptionsSerializer(serializers.Serializer):
    """Options for Excel exports"""
    include_summary_sheet = serializers.BooleanField(default=True)
    include_materials_sheet = serializers.BooleanField(default=True)
    include_machinery_sheet = serializers.BooleanField(default=True)
    include_labor_sheet = serializers.BooleanField(default=True)
    include_charts = serializers.BooleanField(default=True)
    separate_suppliers = serializers.BooleanField(default=False)
    include_price_history = serializers.BooleanField(default=False)