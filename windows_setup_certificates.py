"""
Windows Certificate Generator for WinLink
Generates self-signed certificates for TLS testing on Windows
"""

import os
import sys
from pathlib import Path

def generate_certificates():
    """Generate self-signed certificates using Python cryptography library"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        import ipaddress
        
        print("🔐 Generating self-signed certificates for Windows...")
        
        # Create SSL directory
        ssl_dir = Path("ssl")
        ssl_dir.mkdir(exist_ok=True)
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate subject
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Windows"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WinLink"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        # Create certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv6Address("::1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write private key
        key_path = ssl_dir / "server.key"
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        cert_path = ssl_dir / "server.crt"
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"✅ Certificates generated:")
        print(f"   Private key: {key_path}")
        print(f"   Certificate: {cert_path}")
        print(f"   Valid for: 365 days")
        
        return True
        
    except ImportError:
        print("❌ Cryptography library not installed. Installing...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
            print("✅ Cryptography installed. Please run this script again.")
            return False
        except subprocess.CalledProcessError:
            print("❌ Failed to install cryptography. Please install manually:")
            print("   pip install cryptography")
            return False
    
    except Exception as e:
        print(f"❌ Certificate generation failed: {e}")
        return False

def main():
    print("🪟 WinLink Windows Certificate Generator")
    print("=" * 40)
    
    if generate_certificates():
        print("\n🎉 Certificate generation completed!")
        print("\nYou can now enable TLS in your WinLink configuration.")
    else:
        print("\n⚠️  Certificate generation failed.")
        print("TLS features will be disabled until certificates are available.")

if __name__ == "__main__":
    main()