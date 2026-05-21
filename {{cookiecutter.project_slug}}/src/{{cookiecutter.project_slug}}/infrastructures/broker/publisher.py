{% if cookiecutter.use_broker == "kafka" %}
from dataclasses import dataclass, field
import json
from typing import final

import structlog
from faststream.kafka import KafkaBroker

from {{cookiecutter.project_slug}}.application.dtos.artifact import ArtifactAdmissionNotificationDTO
from {{cookiecutter.project_slug}}.application.interfaces.message_broker import MessageBrokerPublisherProtocol
from {{cookiecutter.project_slug}}.infrastructures.mappers.artifact import InfrastructureArtifactMapper


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MessageBrokerPublisher(MessageBrokerPublisherProtocol):
    """Kafka implementation of MessageBrokerPublisherProtocol."""

    broker: KafkaBroker
    mapper: InfrastructureArtifactMapper
    topic: str = field(default="new_artifacts")

    async def publish_new_artifact(
        self, artifact: ArtifactAdmissionNotificationDTO
    ) -> None:
        try:
            artifact_dict = self.mapper.to_admission_notification_dict(artifact)
            await self.broker.publish(
                json.dumps(artifact_dict, ensure_ascii=False),
                topic=self.topic,
                key=artifact_dict["inventory_id"].encode(),
            )
        except Exception as e:
            logger = structlog.get_logger(__name__)
            logger.error("Failed to publish artifact", error=str(e))
            raise
{% elif cookiecutter.use_broker == "rabbitmq" %}
from dataclasses import dataclass, field
import json
from typing import final

import structlog
from faststream.rabbit import RabbitBroker

from {{cookiecutter.project_slug}}.application.dtos.artifact import ArtifactAdmissionNotificationDTO
from {{cookiecutter.project_slug}}.application.interfaces.message_broker import MessageBrokerPublisherProtocol
from {{cookiecutter.project_slug}}.infrastructures.mappers.artifact import InfrastructureArtifactMapper


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MessageBrokerPublisher(MessageBrokerPublisherProtocol):
    """RabbitMQ implementation of MessageBrokerPublisherProtocol."""

    broker: RabbitBroker
    mapper: InfrastructureArtifactMapper
    queue: str = field(default="new_artifacts")

    async def publish_new_artifact(
        self, artifact: ArtifactAdmissionNotificationDTO
    ) -> None:
        try:
            artifact_dict = self.mapper.to_admission_notification_dict(artifact)
            await self.broker.publish(
                json.dumps(artifact_dict, ensure_ascii=False),
                queue=self.queue,
            )
        except Exception as e:
            logger = structlog.get_logger(__name__)
            logger.error("Failed to publish artifact", error=str(e))
            raise
{% elif cookiecutter.use_broker == "nats" %}
from dataclasses import dataclass, field
import json
from typing import final

import structlog
from faststream.nats import NatsBroker

from {{cookiecutter.project_slug}}.application.dtos.artifact import ArtifactAdmissionNotificationDTO
from {{cookiecutter.project_slug}}.application.interfaces.message_broker import MessageBrokerPublisherProtocol
from {{cookiecutter.project_slug}}.infrastructures.mappers.artifact import InfrastructureArtifactMapper


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MessageBrokerPublisher(MessageBrokerPublisherProtocol):
    """NATS implementation of MessageBrokerPublisherProtocol."""

    broker: NatsBroker
    mapper: InfrastructureArtifactMapper
    subject: str = field(default="new_artifacts")

    async def publish_new_artifact(
        self, artifact: ArtifactAdmissionNotificationDTO
    ) -> None:
        try:
            artifact_dict = self.mapper.to_admission_notification_dict(artifact)
            await self.broker.publish(
                json.dumps(artifact_dict, ensure_ascii=False),
                subject=self.subject,
            )
        except Exception as e:
            logger = structlog.get_logger(__name__)
            logger.error("Failed to publish artifact", error=str(e))
            raise
{% else %}
from dataclasses import dataclass
from typing import final

import structlog

from {{cookiecutter.project_slug}}.application.dtos.artifact import ArtifactAdmissionNotificationDTO
from {{cookiecutter.project_slug}}.application.interfaces.message_broker import MessageBrokerPublisherProtocol


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MessageBrokerPublisher(MessageBrokerPublisherProtocol):
    """No-op publisher (used when no message broker is configured)."""

    async def publish_new_artifact(
        self, artifact: ArtifactAdmissionNotificationDTO
    ) -> None:
        logger = structlog.get_logger(__name__)
        logger.debug("No broker configured; skipping publish_new_artifact")
{% endif %}
