import { SERVICES } from "../config/services";

export function formatTicket(code, serviceType) {
  const service = SERVICES.find((s) => s.type === serviceType);
  const prefix = service ? service.prefix : "";
  return `${prefix}${String(code).padStart(3, "0")}`;
}