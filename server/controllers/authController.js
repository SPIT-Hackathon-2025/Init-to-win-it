import CompanyData from "../models/CompanyData.js";
import jwt from 'jsonwebtoken';
import "dotenv/config";

export const login = async (req, res) => {
    const { companyEmail, password } = req.body;

    try {
        const user = await CompanyData.findOne({ companyEmail });
        if (!user || user.password !== password) {
            return res.status(401).json({ message: "Invalid credentials" });
        }

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '2d' });

        res.status(200).json({ message: "Login successful", user, token });
    } catch (error) {
        res.status(500).json({ message: "Server error", error });
    }
};

export const register = async (req, res) => {
    const companyData = req.body;

    try {
        const newCompany = new CompanyData(companyData);
        await newCompany.save();
        res.status(201).json({ message: "Registration successful", newCompany });
    } catch (error) {
        res.status(500).json({ message: "Server error", error });
    }
};