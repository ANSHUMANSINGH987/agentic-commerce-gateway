import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from google import genai
from sqlalchemy import inspect, text
from src.database import AsyncSessionLocal, engine
from src.models.domain import Base, Product

# Initialize Gemini Client for embeddings
client = genai.Client()

async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using the official Gemini embedding model."""
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
    )
    return [e.values for e in response.embeddings]

async def main():
    print("Initializing production catalog generation...")

    # 1. Ensure pgvector extension and rebuild schema for 3072 dimensions
    async with engine.begin() as conn:
        print("Ensuring pgvector extension exists...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        print("Resetting schema to apply 3072 vector dimensions...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 2. Inspect valid columns dynamically to prevent keyword mismatch
    mapper = inspect(Product)
    valid_columns = {c.key for c in mapper.columns}
    print(f"Detected Product table columns: {valid_columns}")
    
    # 36 Production SKUs
    skus = [
        {"name": "Neural-Link Smartwatch Pro", "base_price": 299.99, "stock_count": 45, "description": "Advanced biometric tracking with neural gesture recognition and AMOLED curved display."},
        {"name": "Quantum Noise-Canceling Earbuds", "base_price": 199.99, "stock_count": 80, "description": "Immersive spatial audio with adaptive environment listening and 40-hour battery life."},
        {"name": "Holo-Lens Developer Edition", "base_price": 899.99, "stock_count": 15, "description": "Mixed reality headset featuring ultra-low latency spatial mapping and high-res micro-OLED."},
        {"name": "Cyber-Deck Portable Terminal", "base_price": 1299.99, "stock_count": 10, "description": "Ruggedized mobile workstation designed for field engineers and decentralized node operators."},
        {"name": "Omni-Charging Power Station 100W", "base_price": 89.99, "stock_count": 120, "description": "GaN fast-charging multi-port hub with real-time wattage telemetry display."},
        {"name": "Titanium Mechanical Keyboard", "base_price": 179.99, "stock_count": 60, "description": "Hot-swappable tactile switches with customizable RGB macro keys and dual wireless modes."},
        {"name": "Edge-AI NPU Accelerator Module", "base_price": 149.99, "stock_count": 50, "description": "Compact peripheral card designed for real-time YOLOv8 and local transformer execution."},
        {"name": "Radxa ZERO 3W Dev Board", "base_price": 45.00, "stock_count": 200, "description": "High-performance credit-card-sized single board computer with NPU acceleration support."},
        {"name": "Raspberry Pi 5 Enterprise Kit", "base_price": 120.00, "stock_count": 90, "description": "Complete edge cluster kit including active cooling, NVMe baseboard, and 8GB RAM."},
        {"name": "Autonomous Drone Flight Controller", "base_price": 349.99, "stock_count": 25, "description": "Open-source autopilot hardware with redundant IMUs and RTK GPS precision module."},
        {"name": "LoRaWAN Long-Range Gateway", "base_price": 220.00, "stock_count": 35, "description": "Industrial IoT gateway for decentralized sensor telemetry and low-power mesh networks."},
        {"name": "Biometric Security YubiKey 5C", "base_price": 55.00, "stock_count": 150, "description": "Multi-protocol hardware authenticator supporting FIDO2, WebAuthn, and OTP."},
        {"name": "Soil Nutrient & Carbon Sensor", "base_price": 210.00, "stock_count": 40, "description": "Real-time telemetry probe measuring soil organic carbon, moisture, and NPK levels."},
        {"name": "Solar-Powered Pest Deterrent Node", "base_price": 130.00, "stock_count": 65, "description": "AI-triggered directional acoustic deterrent for crop protection against wildlife intrusion."},
        {"name": "Autonomous Crop Scouting Drone", "base_price": 1499.99, "stock_count": 8, "description": "Multispectral imaging drone configured for automated NDVI mapping and yield prediction."},
        {"name": "Precision Drip Irrigation Controller", "base_price": 280.00, "stock_count": 30, "description": "Smart valve automation system optimized by local weather and soil moisture forecasts."},
        {"name": "Organic Bio-Enzyme Soil Booster 5L", "base_price": 40.00, "stock_count": 300, "description": "Microbial inoculant designed to accelerate organic carbon sequestration and root growth."},
        {"name": "Agri-Drone Multispectral Camera", "base_price": 750.00, "stock_count": 12, "description": "High-resolution dual-sensor payload capturing RGB and Near-Infrared agricultural indexes."},
        {"name": "Bio-Adaptive Ambient Light Panel", "base_price": 150.00, "stock_count": 70, "description": "Modular LED lighting system syncing automatically with circadian rhythm color temperatures."},
        {"name": "Air-Purifying Botanical Planter", "base_price": 95.00, "stock_count": 55, "description": "Active root-filtration smart planter with integrated air quality sensors and auto-watering."},
        {"name": "Sub-Zero Smart Water Leak Detector", "base_price": 49.99, "stock_count": 110, "description": "Wireless telemetry pod with instant shut-off valve integration and freeze warning alerts."},
        {"name": "Encrypted Smart Door Lock", "base_price": 260.00, "stock_count": 40, "description": "Biometric and NFC deadbolt supporting temporary token generation for agentic deliveries."},
        {"name": "Autonomous Robotic Floor Cleaner", "base_price": 499.99, "stock_count": 20, "description": "LiDAR-navigated vacuum and mop unit featuring self-emptying base station and obstacle AI."},
        {"name": "Acoustic Privacy Sound Masker", "base_price": 85.00, "stock_count": 85, "description": "Dynamic frequency generator designed to protect confidential conversations in open spaces."},
        {"name": "Weather-Adaptive Thermal Jacket", "base_price": 240.00, "stock_count": 45, "description": "Smart fabric outerwear with phase-change insulation and integrated USB-C heating zones."},
        {"name": "Anti-Theft Commuter Backpack 30L", "base_price": 135.00, "stock_count": 90, "description": "Slash-resistant pack featuring RFID-blocking compartments and concealed charging ports."},
        {"name": "Ergonomic Posture-Tracking Tee", "base_price": 65.00, "stock_count": 120, "description": "Embedded weave sensors providing gentle haptic feedback for continuous spine alignment."},
        {"name": "Hydro-Shield All-Terrain Boots", "base_price": 185.00, "stock_count": 60, "description": "Gore-Tex lined tactical footwear built for rugged field operations and variable terrain."},
        {"name": "Modular Everyday Sling Bag", "base_price": 75.00, "stock_count": 140, "description": "Compact cross-body carry system with customizable dividers and weather-sealed zippers."},
        {"name": "UV-Reactive Performance Hoodie", "base_price": 90.00, "stock_count": 100, "description": "Lightweight athletic layer with built-in UPF 50+ protection and active moisture wicking."},
        {"name": "Mastering Agentic AI Systems", "base_price": 59.99, "stock_count": 250, "description": "Comprehensive guide to building production multi-agent architectures and tool-use gateways."},
        {"name": "PostgreSQL & Vector Search Handbook", "base_price": 49.99, "stock_count": 180, "description": "Advanced guide covering pgvector indexing, semantic query tuning, and hybrid search pipelines."},
        {"name": "Modern FastAPI & Async Architecture", "base_price": 45.00, "stock_count": 210, "description": "Deep dive into high-concurrency microservices, asyncpg optimization, and robust CI/CD."},
        {"name": "The Architecture of Decentralized Commerce", "base_price": 65.00, "stock_count": 130, "description": "Exploration of autonomous payment gateways, cryptographic receipts, and agentic workflows."},
        {"name": "Python Concurrency Patterns & Internals", "base_price": 52.00, "stock_count": 160, "description": "Practical manual on asyncio event loops, greenlets, and threading performance tuning."},
        {"name": "Ethics and Governance in Autonomous AI", "base_price": 39.99, "stock_count": 190, "description": "Frameworks for safety alignment, verifiable audit logs, and risk mitigation in agentic agents."}
    ]

    print(f"Generated {len(skus)} SKUs. Batch-processing embeddings...")

    descriptions = [sku["description"] for sku in skus]
    batch_size = 18
    all_embeddings = []

    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i:i + batch_size]
        try:
            embeddings = await generate_embeddings_batch(batch)
            all_embeddings.extend(embeddings)
            print(f"Embedded batch {i // batch_size + 1}")
            await asyncio.sleep(4)
        except Exception as e:
            print(f"Error embedding batch: {e}")
            return

    # 3. Populate database
    print("Populating database...")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for index, sku in enumerate(skus):
                sku_data = {
                    "name": sku["name"],
                    "base_price": sku["base_price"],
                    "stock_count": sku["stock_count"],
                    "description": sku["description"],
                    "embedding": all_embeddings[index]
                }
                filtered_data = {k: v for k, v in sku_data.items() if k in valid_columns}
                product = Product(**filtered_data)
                session.add(product)
            
            await session.commit()

    print("Production Supabase database successfully seeded!")

if __name__ == "__main__":
    asyncio.run(main())