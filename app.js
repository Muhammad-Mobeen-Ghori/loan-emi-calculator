const express = require("express");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const os = require("os");
const path = require("path");

dotenv.config();

const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// MongoDB connection
mongoose.connect(process.env.MONGO_URL)
    .then(() => {
        console.log("MongoDB connected successfully");
    })
    .catch((error) => {
        console.error("MongoDB connection failed:", error.message);
    });

// MongoDB Schema
const calculationSchema = new mongoose.Schema({
    principal: {
        type: Number,
        required: true
    },
    rate: {
        type: Number,
        required: true
    },
    months: {
        type: Number,
        required: true
    },
    emi: {
        type: Number,
        required: true
    },
    servedBy: {
        type: String,
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

const Calculation = mongoose.model(
    "Calculation",
    calculationSchema,
    "calculations"
);

// Get application pod IP
function getPodIP() {
    if (process.env.POD_IP) {
        return process.env.POD_IP;
    }

    const interfaces = os.networkInterfaces();

    for (const interfaceName of Object.keys(interfaces)) {
        for (const address of interfaces[interfaceName]) {
            if (address.family === "IPv4" && !address.internal) {
                return address.address;
            }
        }
    }

    return "127.0.0.1";
}

// POST /api/emi
app.post("/api/emi", async (req, res) => {
    try {
        const { P, rate, n } = req.body;

        // Server-side validation
        if (
            typeof P !== "number" ||
            typeof rate !== "number" ||
            typeof n !== "number" ||
            !Number.isFinite(P) ||
            !Number.isFinite(rate) ||
            !Number.isFinite(n) ||
            P <= 0 ||
            rate <= 0 ||
            n <= 0
        ) {
            return res.status(400).json({
                error: "Principal, interest rate and tenure must be positive numbers."
            });
        }

        if (!Number.isInteger(n)) {
            return res.status(400).json({
                error: "Tenure must be a positive whole number of months."
            });
        }

        // EMI calculation
        const r = rate / 12 / 100;

        const emi = (
            P * r * Math.pow(1 + r, n)
        ) / (
            Math.pow(1 + r, n) - 1
        );

        const totalPayment = emi * n;
        const totalInterest = totalPayment - P;

        // Identify serving pod
        const servedBy = process.env.HOSTNAME || os.hostname();
        const podIP = getPodIP();

        // Save calculation in MongoDB
        const calculation = new Calculation({
            principal: P,
            rate: rate,
            months: n,
            emi: Number(emi.toFixed(2)),
            servedBy: servedBy,
            createdAt: new Date()
        });

        await calculation.save();

        // Return JSON response
        res.json({
            principal: P,
            rate: rate,
            months: n,
            emi: Number(emi.toFixed(2)),
            totalPayment: Number(totalPayment.toFixed(2)),
            totalInterest: Number(totalInterest.toFixed(2)),
            servedBy: servedBy,
            podIP: podIP
        });

    } catch (error) {
        console.error("EMI calculation error:", error);

        res.status(500).json({
            error: "Unable to calculate EMI. Please try again."
        });
    }
});

// GET /api/history
app.get("/api/history", async (req, res) => {
    try {
        const history = await Calculation.find()
            .sort({ createdAt: -1 })
            .limit(10)
            .lean();

        res.json(history);

    } catch (error) {
        res.status(500).json({
            error: "Unable to retrieve calculation history."
        });
    }
});

// GET /health
app.get("/health", async (req, res) => {
    try {
        await mongoose.connection.db.admin().ping();

        res.status(200).json({
            status: "healthy",
            mongodb: "connected"
        });

    } catch (error) {
        res.status(503).json({
            status: "unhealthy",
            mongodb: "disconnected"
        });
    }
});

// Start server
const PORT = process.env.PORT || 3000;

app.listen(PORT, "0.0.0.0", () => {
    console.log(`Loan EMI Calculator running on port ${PORT}`);
});
