const fakeQueue = [
  { id: 1, number: "A001", service: "Boxes" },
  { id: 2, number: "B001", service: "Shipping and Parcel" },
  { id: 3, number: "A002", service: "Shipping and Parcel" },
];

export async function callNextCustomer() {
  await new Promise((r) => setTimeout(r, 300)); // simulates the network
  return fakeQueue.shift() ?? null;             // null = queue is empty
}