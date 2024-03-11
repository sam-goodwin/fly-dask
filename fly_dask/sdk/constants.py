from enum import Enum

# @see https://github.com/bwhli/fly-python-sdk/blob/main/fly_python_sdk/constants.py


class FlyRegion(Enum):
    AMS = "ams"  # Amsterdam, Netherlands
    ARN = "arn"  # Stockholm, Sweden
    BOG = "bog"  # Bogotá, Colombia
    BOS = "bos"  # Boston, Massachusetts (US)
    CDG = "cdg"  # Paris, France
    DEN = "den"  # Denver, Colorado (US)
    DFW = "dfw"  # Dallas, Texas (US)
    EWR = "ewr"  # Secaucus, NJ (US)
    FRA = "fra"  # Frankfurt, Germany
    GDL = "gdl"  # Guadalajara, Mexico
    GIG = "gig"  # Rio de Janeiro, Brazil
    GRU = "gru"  # São Paulo
    HKG = "hkg"  # Hong Kong, Hong Kong
    IAD = "iad"  # Ashburn, Virginia (US)
    JNB = "jnb"  # Johannesburg, South Africa
    LAX = "lax"  # Los Angeles, California (US
    LHR = "lhr"  # London, United Kingdom
    MAA = "maa"  # Chennai (Madras), India
    MAD = "mad"  # Madrid, Spain
    MIA = "mia"  # Miami, Florida (US)
    NRT = "nrt"  # Tokyo, Japan
    ORD = "ord"  # Chicago, Illinois (US)
    OTP = "otp"  # Bucharest, Romania
    QRO = "qro"  # Querétaro, Mexico
    SCL = "scl"  # Santiago, Chile
    SEA = "sea"  # Seattle, Washington (US)
    SIN = "sin"  # Singapore, Singapore
    SJC = "sjc"  # San Jose, California (US)
    SYD = "syd"  # Sydney, Australia
    WAW = "waw"  # Warsaw, Poland
    YUL = "yul"  # Montreal, Canada
    YYZ = "yyz"  # Toronto, Canada


class MachineSize(Enum):
    SHARED_CPU_1X = "shared-cpu-1x"
    DEDICATED_CPU_1X = "dedicated-cpu-1x"
    DEDICATED_CPU_2X = "dedicated-cpu-2x"
    DEDICATED_CPU_4X = "dedicated-cpu-4x"
    DEDICATED_CPU_8X = "dedicated-cpu-8x"
    SHARED_CPU_2X = "shared-cpu-2x"
    SHARED_CPU_4X = "shared-cpu-4x"
    SHARED_CPU_8X = "shared-cpu-8x"
    PERFORMANCE_1X = "performance-1x"
    PERFORMANCE_2X = "performance-2x"
    PERFORMANCE_4X = "performance-4x"
    PERFORMANCE_8X = "performance-8x"
    PERFORMANCE_16X = "performance-16x"
