#!/bin/bash

echo ""
echo "========================================="
echo "   FastAPI Module 6 - Practice Launcher  "
echo "========================================="
echo ""
echo "  1)  Practice 1 - First REST API"
echo "  2)  Practice 2 - Defining Models"
echo "  3)  Practice 3 - Edit Objects"
echo "  4)  Practice 4 - Basic Auth"
echo "  5)  Practice 5 - User Registration"
echo "  6)  Practice 6 - Password Hashing"
echo "  7)  Practice 7 - OAuth2 + JWT"
echo ""
read -p "Select a practice (1-7): " choice

case $choice in
    1|2|3|4|5|6|7)
        echo ""
        echo "  Starting Practice $choice..."
        echo ""
        fastapi dev src/practice_$choice.py
        ;;
    *)
        echo ""
        echo "  Invalid option '$choice'. Please select a number between 1 and 7."
        exit 1
        ;;
esac
