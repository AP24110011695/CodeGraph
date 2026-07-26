"""Pydantic schemas for the API documentation API responses."""

from pydantic import BaseModel, Field


class EndpointSchema(BaseModel):
    """Schema for a detected API endpoint."""

    method: str = Field(description="HTTP method (GET, POST, PUT, DELETE, PATCH)")
    path: str = Field(description="Route path")
    handler: str = Field(description="Handler function name")
    controller: str | None = Field(default=None, description="Controller/class name")
    authentication: str | None = Field(default=None, description="Authentication type")
    middleware: list[str] = Field(default_factory=list, description="Middleware names")
    request: str | None = Field(default=None, description="Request model/type")
    response: str | None = Field(default=None, description="Response model/type")
    tags: list[str] = Field(default_factory=list, description="Endpoint tags")
    parameters: list[dict] = Field(default_factory=list, description="Parameters")
    query_params: list[str] = Field(default_factory=list, description="Query parameter names")
    path_params: list[str] = Field(default_factory=list, description="Path parameter names")
    file_path: str = Field(default="", description="Source file path")


class ApiDocResponse(BaseModel):
    """Complete response returned by POST /apidocs/{upload_id}."""

    framework: str = Field(description="Detected API framework")
    total_endpoints: int = Field(description="Total number of detected endpoints")
    endpoints: list[EndpointSchema] = Field(description="List of detected endpoints")
