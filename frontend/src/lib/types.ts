export interface TokenResponse {
  access_token: string;
  username: string | null;
}

export interface Product {
  code: string;
  name: string;
  category: string | null;
  created_at: string;
}

export interface ForecastReport {
  product_id: string;
  predicted_demand: number;
  based_on_events: number;
  confidence_interval: [number, number];
  trend: string;
  source: string;
}

export interface ProductOverview {
  product_id: string;
  current_stage: string | null;
  last_event_at: string | null;
  events_count: number;
  forecast: ForecastReport;
}

export type EventType = "sensor" | "stage_change";

export interface TrackingEvent {
  event_type: EventType;
  product_id: string;
  stage: string;
  timestamp: string;
  details: Record<string, string | number>;
}

export interface RouteStop {
  sequence: number;
  location: string;
  notes: string | null;
}

export type RouteAction = "dispatch" | "deliver" | "cancel";
export type RouteStatus = "planned" | "in_transit" | "delivered" | "cancelled";

export interface Route {
  route_id: number;
  vehicle_type: string;
  refrigerated: boolean;
  departure_date: string;
  stops: RouteStop[];
  total_distance_km: number | null;
  notes: string | null;
  status: RouteStatus;
  status_label: string;
  allowed_actions: RouteAction[];
}

export interface StrategyResult {
  strategy: string;
  description: string;
  stops: string[];
  total_distance_km: number;
}

export interface LocationItem {
  name: string;
  latitude: number;
  longitude: number;
}

export interface VehicleType {
  code: string;
  refrigerated: boolean;
}

export interface Corridor {
  name: string;
  total_distance_km: number;
  routes: string[];
}

export interface DemandRecord {
  product_id: string;
  period: string;
  quantity: number;
}

export interface ForecastModel {
  name: string;
  label: string;
  min_points: number;
}

export interface ForecastPlan {
  product_id: string;
  model: string;
  predicted_demand: number;
  based_on_records: number;
  generated_at: string;
  can_undo: boolean;
}

export interface CommandLogEntry {
  command: string;
  product_id: string;
  executed_at: string;
  undone: boolean;
}

export interface Vendor {
  code: string;
  label: string;
  sensor_type: string;
  unit: string;
  accepts_simulated_value: boolean;
}

export interface IngestResult {
  product_id: string;
  sensor_type: string;
  reading_value: number;
  unit: string;
  notified_via: string;
  message: string;
  device_id: string | null;
}

export interface Reading {
  device_id: string;
  sensor_type: string;
  value: number;
  unit: string;
  product_id: string;
  stage: string;
  received_at: string;
}

export interface Alert {
  device_id: string;
  sensor_type: string;
  value: number;
  unit: string;
  product_id: string;
  message: string;
  raised_at: string;
}

export interface Device {
  device_id: string;
  sensor_type: string;
  last_value: number;
  unit: string;
  last_product_id: string;
  last_seen_at: string;
  readings_count: number;
}
