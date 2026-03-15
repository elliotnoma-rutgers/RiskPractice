# Swap simulator using CIR
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter

# -----------------------------
# PARAMETERS
# -----------------------------

np.random.seed(1)

n_paths = 200
n_steps = 60
T = 5.0
dt = T / n_steps
times = np.linspace(0, T, n_steps)

# CIR parameters
a = 0.6       # mean reversion speed
b = 0.03      # long term rate
sigma = 0.1   # volatility
r0 = 0.02

# swap parameters
notional = 1_000_000
fixed_rate = 0.025

# credit parameters
recovery = 0.4
hazard_rate = 0.02


# -----------------------------
# SIMULATE INTEREST RATES (CIR)
# -----------------------------

rates = np.zeros((n_paths, n_steps))
rates[:,0] = r0

for i in range(1, n_steps):

    z = np.random.normal(size=n_paths)

    r_prev = rates[:, i-1]

    dr = a*(b - r_prev)*dt + sigma*np.sqrt(np.maximum(r_prev,0))*np.sqrt(dt)*z

    r_new = r_prev + dr

    # enforce positivity
    rates[:, i] = np.maximum(r_new, 0)


# -----------------------------
# SWAP MTM CALCULATION
# -----------------------------

def swap_value(rate_path, t_index):

    remaining = times[t_index:]
    if len(remaining) == 0:
        return 0

    r = rate_path[t_index]

    discount = np.exp(-r*(remaining - times[t_index]))

    floating_leg = notional*(1 - discount[-1])
    fixed_leg = notional * fixed_rate * np.sum(discount)*dt

    return floating_leg - fixed_leg


# -----------------------------
# COMPUTE EXPOSURES
# -----------------------------

exposures = np.zeros((n_paths, n_steps))

for p in range(n_paths):
    for t in range(n_steps):

        v = swap_value(rates[p], t)
        exposures[p,t] = max(v,0)


# -----------------------------
# EXPECTED EXPOSURE
# -----------------------------

EE = exposures.mean(axis=0)


# -----------------------------
# CVA CALCULATION
# -----------------------------

survival = np.exp(-hazard_rate * times)
default_prob = np.diff(np.insert(1-survival,0,0))

discount = np.exp(-r0*times)

CVA = (1-recovery) * np.sum(EE * default_prob * discount)

print("CVA:", CVA)


# -----------------------------
# VIDEO GENERATION
# -----------------------------

fig, ax = plt.subplots(figsize=(8,5))

writer = FFMpegWriter(fps=5)

with writer.saving(fig, "cir_exposure_simulation.mp4", dpi=150):

    for step in range(2, n_steps):

        ax.clear()

        # exposure paths - only plot a subset for clarity    
        for p in range(min(50, n_paths)):
            ax.plot(times[:step], exposures[p,:step],
                    color="lightgray", alpha=0.5)

        # expected exposure
        ax.plot(times[:step], EE[:step],
                color="red", linewidth=3, label="Expected Exposure")

        ax.set_title(f"CIR Monte Carlo Exposure\nCVA ≈ {CVA:,.0f}")
        ax.set_xlabel("Time (Years)")
        ax.set_ylabel("Exposure")
        ax.legend()

        writer.grab_frame()

print("Video saved: cir_exposure_simulation.mp4")