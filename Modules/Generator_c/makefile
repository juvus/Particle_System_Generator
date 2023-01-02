#==============================================================================================
# Makefile for the compilation of:
#	1) Artificial particles generator (generator_c.exe);
#   2) Particle shared library (particle.dll);
#   3) PSOAlg shared library (PSOAlg.dll). 
# Author: Dmitry Safonov
# Organization: Lappeenranta-Lahti University of Technology LUT
# Date: 24.12.2020
#==============================================================================================

CC = gcc
CFLAGS = -c -Wall -o
LFLAGS = -s -o
LFLAGS_DLL = -s -fPIC -shared -o
SDIR = src
ODIR = build/obj
DDIR = data
EDIR = build
IDIR = include
LDIR = lib
LIBS = 

all: Directories generator_c particle.dll pso_algorithm.dll

#==============================================================================================
# Rule for creating neccessary directories
#==============================================================================================

.PHONY: Directories
Directories:
	mkdir -p build
	mkdir -p build/obj
	mkdir -p data

#==============================================================================================
# Dependences (for further creating the object *.o files):
#==============================================================================================

# Main code of the artificial particles generator 
_DEPS_generator_c = data_types.h get_particle_parameters.h PSOAlgorithm.h distribution_treatment.h
DEPS_generator_c = $(patsubst %,$(IDIR)/%,$(_DEPS_generator_c))

# Module for the distribution treatment
_DEPS_distribution_treatment = 
DEPS_distribution_treatment = $(patsubst %,$(IDIR)/%,$(_DEPS_distribution_treatment))

# Module for calculating the particles parameters
_DEPS_get_particle_parameters = data_types.h sort_array.h
DEPS_get_particle_parameters = $(patsubst %,$(IDIR)/%,$(_DEPS_get_particle_parameters))

# Module for running the PSO search algorithm
_DEPS_PSOAlgorithm = data_types.h get_particle_parameters.h
DEPS_PSOAlgorithm = $(patsubst %,$(IDIR)/%,$(_DEPS_PSOAlgorithm))

# Module for array sorting with quicksort algorithm
_DEPS_sort_array = 
DEPS_sort_array = $(patsubst %,$(IDIR)/%,$(_DEPS_sort_array))

#==============================================================================================
# Rules for compilation of the object *.o files:
#==============================================================================================

$(ODIR)/%.o: $(SDIR)/%.c $(DEPS_%) 
	$(CC) $(CFLAGS) $@ $< -I$(IDIR)

#==============================================================================================
# Rules for the linker:
#==============================================================================================

_OBJ_GENERATOR = distribution_treatment.o generator_c.o get_particle_parameters.o PSOAlgorithm.o \
sort_array.o
OBJ_GENERATOR = $(patsubst %,$(ODIR)/%,$(_OBJ_GENERATOR))

generator_c: $(OBJ_GENERATOR)
	$(CC) $(LFLAGS) $(EDIR)/$@ $^ -L$(LDIR) $(LIBS)
	ctags -f ./TAGS -e -R ./include ./src
	ctags -f ./src/TAGS -e -R ./include ./src


_OBJ_PARTICLE = get_particle_parameters.o sort_array.o
OBJ_PARTICLE = $(patsubst %,$(ODIR)/%,$(_OBJ_PARTICLE))

particle.dll: $(OBJ_PARTICLE)
	$(CC) $(LFLAGS_DLL) $(EDIR)/$@ $^ -L$(LDIR) $(LIBS)


_OBJ_PSOALG = PSOAlgorithm.o get_particle_parameters.o sort_array.o
OBJ_PSOALG = $(patsubst %,$(ODIR)/%,$(_OBJ_PSOALG))

pso_algorithm.dll: $(OBJ_PSOALG)
	$(CC) $(LFLAGS_DLL) $(EDIR)/$@ $^ -L$(LDIR) $(LIBS)

#==============================================================================================
# Rules for the clean the build firectory:
#==============================================================================================

.PHONY: clean
clean:
	rm -f $(ODIR)/*.o
