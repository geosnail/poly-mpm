import os
from numpy import pi,array,dot,tan,zeros,eye,cumsum,outer,sum,trace,exp
from numpy import linspace,tile,repeat
import matplotlib.pyplot as plt

class Params():
    def __init__(self,mode):
        self.dt = 1e-3 # timestep (s)
        self.t = 0. # physical time (s)
        self.tstep = 0 # current timestep
        self.t_f = 2.#100*self.dt # final time (s)
        self.savetime = .1
        self.nt = int(self.t_f/self.dt) # number of timesteps - WRONG!
        self.save = 0 # save counter
        self.M_tol = 1e-10 # very small mass (kg)
        self.max_g = 0. # gravity (ms^-2)
        self.max_q = 2.
        self.update_forces()
        self.theta = 0.*pi/180. # slope angle (degrees)
        self.G = Grid_Params()
        self.B = Boundary_Params()
        self.O = Output_Params(self.nt)
        self.S = Solid_Params(self.G)
        self.F = Fluid_Params()
        self.R = Fluid_Params()
        self.check_positions = False
        self.has_yielded = False
        self.damping = True # local non-viscous damping
        self.mode = mode
        
    def update_forces(self):
        t_c = .5
        self.g = self.max_g*(1.-exp(-3.*self.t**2/t_c**2))
        self.q = self.max_q*(1.-exp(-3.*self.t**2/t_c**2))

class Grid_Params():
    def __init__(self):
        self.scale = 2 # grid points per m
        self.thickness = 1. # (m) into page
        self.x_m = 0.0 # (m)
        self.x_M = 12.0 # (m)
        self.y_m = 0.0 # (m)
        self.y_M = 6.0 # (m)
        self.nx = int(self.x_M-self.x_m)*self.scale+1
        self.ny = int(self.y_M-self.y_m)*self.scale+1
        self.x = linspace(self.x_m,self.x_M,self.nx)
        self.y = linspace(self.y_m,self.y_M,self.ny)
        self.dx = self.x[1] - self.x[0] # grid spacing (m)
        self.dy = self.y[1] - self.y[0] # grid spacing (m)

class Boundary_Params():
    def __init__(self):
        self.wall = False
        self.has_top = False
        self.has_bottom = True
        self.has_right = True
        self.has_left = True
        self.outlet_left = False
        self.force_boundaries = True
        self.vertical_force = True
        self.horizontal_force = False
        self.roughness = False

class Solid_Params():
    def __init__(self,G):
        self.X = []
        self.Y = []
        self.pts_per_cell = 3
        self.x = (G.nx-1)*self.pts_per_cell # particles in x direction
        self.y = (G.ny-1)*self.pts_per_cell # particles in y direction
        self.n = 0

        self.mode = 'slope' # ball, blob, slope, excavate
#        self.law = 'elastic'
        self.law = 'von_mises'
        self.rho = 2650. # density (kg/m^3)
        
        self.E = 1.e7 # elastic modulus (Pa)
        self.nu = 0.3 # poisson's ratio
        self.K = self.E/(3.*(1.-2.*self.nu)) # bulk modulus (Pa)
        self.G = self.E/(2.*(1.+self.nu)) # shear modulus (Pa)

        self.s = 50.
        self.k = 1.

        self.slope_angle = 90.
        self.corner = array((3.,3.,0))    
        gap = array((G.dx,G.dy))/(2*self.pts_per_cell)
        m = tan(self.slope_angle*pi/180.) # slope gradient
        xp = linspace(G.x_m+gap[0],G.x_M-gap[0],self.x)
        yp = linspace(G.y_m+gap[1],G.y_M-gap[1],self.y)
        X = tile(xp,self.y)
        Y = repeat(yp,self.x)
        for i in xrange(self.x*self.y):
            if (X[i] > self.corner[0] or
                Y[i] < self.corner[1]):
                if not ((X[i]>self.corner[0]) and
                       Y[i]>m*(X[i]-self.corner[0])+self.corner[1]):
                    self.X.append(X[i])
                    self.Y.append(Y[i])
                    self.n += 1
        total_area = (G.x_M-G.x_m)*(G.y_M-G.y_m)
        missing_corner = (self.corner[0] - G.x_m)*(G.y_M-self.corner[1])
        self.A = (total_area - missing_corner)/self.n # area (m^2)


class Output_Params():
    def __init__(self,nt):
        self.measure_energy = True
        self.plot_continuum = True
        self.plot_material_points = True
        self.plot_gamma_dot = False
        self.plot_fluid = False
        self.measure_stiffness = False
        self.check_positions = False
        self.plot_fluid = False
        self.energy = zeros((10*nt+1,4)) # DON'T KNOW NUMBER OF TIMESTEPS!

class Fluid_Params():
    def __init__(self):
        self.n = 0
        
class Rigid_Params():
    def __init__(self):
        self.n = 0

