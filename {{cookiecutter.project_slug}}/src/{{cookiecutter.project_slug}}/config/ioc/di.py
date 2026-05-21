from dishka import Provider

from {{cookiecutter.project_slug}}.config.ioc.providers import (
{% if cookiecutter.use_broker != "none" %}
    BrokerProvider,
{% endif %}
    CacheProvider,
    DatabaseProvider,
    HTTPClientProvider,
    MapperProvider,
    RepositoryProvider,
    ServiceProvider,
    SettingsProvider,
    UseCaseProvider,
    UnitOfWorkProvider,
)


def get_providers() -> list[Provider]:
    """Returns the list of Dishka providers for dependency injection."""
    return [
        SettingsProvider(),
        DatabaseProvider(),
        HTTPClientProvider(),
{% if cookiecutter.use_broker != "none" %}
        BrokerProvider(),
{% endif %}
        RepositoryProvider(),
        ServiceProvider(),
        MapperProvider(),
        CacheProvider(),
        UseCaseProvider(),
        UnitOfWorkProvider(),
    ]
