import { Kafka, Consumer, Producer, KafkaConfig } from 'kafkajs';
import { createLogger } from '../utils/logger.js';

const logger = createLogger('kafka');

const brokers = (process.env.KAFKA_BROKERS || 'localhost:9092').split(',');

export const kafkaConfig: KafkaConfig = {
  clientId: process.env.KAFKA_CLIENT_ID || 'api-gateway',
  brokers,
  retry: { retries: 3, initialRetryTime: 300 },
};

export const kafka = new Kafka(kafkaConfig);
export const admin = kafka.admin();
export const producer: Producer = kafka.producer();
export const consumer: Consumer = kafka.consumer({ groupId: 'api-gateway-consumers' });

export async function connectKafka(): Promise<void> {
  try {
    await admin.connect();
    logger.info('Kafka admin connected');

    const topics = await admin.listTopics();
    logger.info('Available topics', { topics });
  } catch (err) {
    logger.warn('Kafka admin connection failed — running in degraded mode', { error: (err as Error).message });
  }

  try {
    await producer.connect();
    logger.info('Kafka producer connected');
  } catch (err) {
    logger.warn('Kafka producer connection failed', { error: (err as Error).message });
  }
}

export async function disconnectKafka(): Promise<void> {
  await producer.disconnect();
  await admin.disconnect();
  logger.info('Kafka disconnected');
}

export async function publishEvent(topic: string, key: string, value: Record<string, unknown>): Promise<void> {
  try {
    await producer.send({
      topic,
      messages: [{ key, value: JSON.stringify(value) }],
    });
    logger.debug(`Event published to ${topic}`, { key });
  } catch (err) {
    logger.error(`Failed to publish to ${topic}`, { error: (err as Error).message });
    throw err;
  }
}