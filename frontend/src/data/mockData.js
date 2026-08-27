export const initialRecommendations = [
  {
    id: "A",
    title: "Air Freight",
    tag: "Fastest",
    cost: 15000,
    deliveryDays: 3,
    risk: "Low",
    score: 92,
    description: "Move the microchip shipment by air to recover most of the 14-day delay.",
    pros: ["Very fast recovery", "Low disruption risk", "Keeps launch date"],
    cons: ["Higher transport cost"],
    confidence: 0.89,
    reasoning: "Historical data shows air freight reduces delay impact by 78% on average. Current capacity available on 3 carriers. Weather risk minimal on this route.",
    financialExposure: 15000,
    inventoryImpact: "+180 units recovered",
    riskReduction: "78% delay mitigation",
    confidenceBreakdown: {
      model: 0.91,
      solver: 0.87,
      constraints: 0.95
    }
  },
  {
    id: "B",
    title: "Secondary Supplier",
    tag: "Balanced",
    cost: 12800,
    deliveryDays: 7,
    risk: "Medium",
    score: 86,
    description: "Purchase from a secondary supplier at a 10% premium.",
    pros: ["Lower than air-freight cost", "Diversifies supplier risk"],
    cons: ["Supplier qualification needed", "Slower than air"],
    confidence: 0.82,
    reasoning: "Secondary supplier has 94% on-time delivery rate. Qualification process adds 2 days. Cost premium within budget tolerance.",
    financialExposure: 12800,
    inventoryImpact: "+120 units recovered",
    riskReduction: "52% delay mitigation",
    confidenceBreakdown: {
      model: 0.84,
      solver: 0.81,
      constraints: 0.88
    }
  },
  {
    id: "C",
    title: "Delay Product Launch",
    tag: "Lowest Cost",
    cost: 5000,
    deliveryDays: 14,
    risk: "High",
    score: 71,
    description: "Accept the delay and move the final product launch date.",
    pros: ["Lowest direct logistics cost", "No emergency procurement"],
    cons: ["Revenue impact", "Customer satisfaction risk"],
    confidence: 0.76,
    reasoning: "Launch delay projected to cost $45K-$120K in lost revenue. Customer churn risk elevated. No supply chain cost beyond admin.",
    financialExposure: 5000,
    inventoryImpact: "No recovery",
    riskReduction: "0% delay mitigation",
    confidenceBreakdown: {
      model: 0.78,
      solver: 0.73,
      constraints: 0.82
    }
  }
];

export const initialHistory = [
  { id: 1, date: "Aug 26, 2026", option: "Air Freight", predicted: 15000, actual: 18000, outcome: "Positive", status: "Completed" },
  { id: 2, date: "Aug 19, 2026", option: "Secondary Supplier", predicted: 12000, actual: 11800, outcome: "Positive", status: "Completed" },
  { id: 3, date: "Aug 05, 2026", option: "Air Freight", predicted: 14000, actual: 15500, outcome: "Positive", status: "Completed" }
];

export const shipmentData = {
  id: "MC-2048",
  product: "Microchips",
  quantity: 500,
  origin: "Taiwan",
  destination: "San Jose, CA",
  etd: "2026-08-20",
  eta: "2026-09-03",
  predictedDelay: 14,
  delayProbability: 0.91,
  riskScore: 91,
  currentStatus: "At Risk",
  financialExposure: 185000,
  inventoryImpact: "Production line stoppage in 7 days",
  riskFactors: [
    { factor: "Port congestion", severity: "High", probability: 0.85 },
    { factor: "Weather disruption", severity: "Medium", probability: 0.42 },
    { factor: "Carrier capacity", severity: "Medium", probability: 0.58 },
    { factor: "Customs delay", severity: "Low", probability: 0.23 }
  ]
};

export const defaultConstraints = {
  budget: 20000,
  inventory: 250,
  maxDeliveryDays: 14,
  allowedRiskLevels: ["Low", "Medium", "High"]
};

export const modelInfo = {
  version: "v1.0",
  type: "XGBoost + SciPy Solver",
  lastRetrained: "2026-08-15",
  nextRetraining: 20,
  accuracy: 0.87,
  status: "Online"
};