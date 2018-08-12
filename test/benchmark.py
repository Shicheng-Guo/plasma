from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals 
from __future__ import absolute_import

import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from . import Finemap, SimAse, Haplotypes
from . import EvalCaviar, EvalCaviarASE

class Benchmark(object):
	dir_path = os.path.dirname(os.path.realpath(__file__))
	res_path = os.path.join("results")
	def __init__(self, params):
		self.params = params
		self.haplotypes = Haplotypes(params)

		self.results = []
		self.results_df = None
		self.primary_var_vals = []
		self.simulation = SimAse(self)

		self.update_model_params()
		self.update_sim_params()

		self.time = datetime.now()
		self.timestamp = self.time.strftime("%y%m%d%H%M%f")
		self.counter = 0
		self.test_count = self.params["test_count"]
		self.count_digits = len(str(self.test_count))

		self.output_folder = self.timestamp + "_" + self.params["test_name"]
		self.output_path = os.path.join(self.dir_path, self.res_path, self.output_folder)

	def update_model_params(self):
		self.model_params = {
			"num_snps_imbalance": self.params["num_snps"],
			"num_snps_total_exp": self.params["num_snps"],
			"num_ppl_imbalance": self.params["num_ppl"],
			"num_ppl_total_exp": self.params["num_ppl"],
			"overdispersion": self.params["overdispersion"]
		}

	def update_sim_params(self):
		self.sim_params = {
			"num_snps": self.params["num_snps"],
			"num_ppl": self.params["num_ppl"],
			# "var_effect_size": self.params["var_effect_size"],
			"overdispersion": self.params["overdispersion"],
			"prop_noise_eqtl": self.params["prop_noise_eqtl"],
			"prop_noise_ase": self.params["prop_noise_ase"],
			# "baseline_exp": self.params["baseline_exp"],
			"num_causal": self.params["num_causal"],
			# "ase_read_prop": self.params["ase_read_prop"],
			"std_fraction": self.params["std_fraction"],
			"coverage": self.params["coverage"]
		}
		self.simulation.update()


	def output_result(self, result, out_dir):
		title_var = self.params["primary_var_display"]
		var_value = str(self.params[self.params["primary_var"]])

		set_sizes_full = result["set_sizes_full"]
		set_sizes_indep = result["set_sizes_indep"]
		set_sizes_eqtl = result["set_sizes_eqtl"]
		set_sizes_ase = result["set_sizes_ase"]
		set_sizes_caviar = result["set_sizes_caviar"]
		set_sizes_caviar_ase = result["set_sizes_caviar_ase"]

		recall_rate_full = result["recall_rate_full"]
		recall_rate_indep = result["recall_rate_indep"]
		recall_rate_eqtl = result["recall_rate_eqtl"]
		recall_rate_ase = result["recall_rate_ase"]
		recall_rate_caviar = result["recall_rate_caviar"]
		recall_rate_caviar_ase = result["recall_rate_caviar_ase"]

		params_str = "\n".join("{:<20}{:>20}".format(k, v) for k, v in self.params.viewitems())
		with open(os.path.join(out_dir, "parameters.txt"), "w") as params_file:
			params_file.write(params_str)

		with open(os.path.join(out_dir, "causal_set_sizes.txt"), "w") as cssfull:
			cssfull.write("\n".join(str(i) for i in set_sizes_full))

		with open(os.path.join(out_dir, "causal_set_sizes_independent.txt"), "w") as cssindep:
			cssindep.write("\n".join(str(i) for i in set_sizes_indep))

		with open(os.path.join(out_dir, "causal_set_sizes_eqtl_only.txt"), "w") as csseqtl:
			csseqtl.write("\n".join(str(i) for i in set_sizes_eqtl))

		with open(os.path.join(out_dir, "causal_set_sizes_ase_only.txt"), "w") as cssase:
			cssase.write("\n".join(str(i) for i in set_sizes_ase))

		with open(os.path.join(out_dir, "causal_set_sizes_caviar_ase.txt"), "w") as csscav:
			csscav.write("\n".join(str(i) for i in set_sizes_caviar))
		
		with open(os.path.join(out_dir, "causal_set_sizes_caviar_ase.txt"), "w") as csscavase:
			csscavase.write("\n".join(str(i) for i in set_sizes_caviar_ase))

		with open(os.path.join(out_dir, "recalls.txt"), "w") as rr:
			rr.write(
				"Full:{:>15}\nIndependent Likelihoods:{:>15}\neQTL-Only:{:>15}\nASE-only:{:>15}\nCAVIAR:{:>15}\nCAVIAR_ASE:{:>15}".format(
					recall_rate_full, 
					recall_rate_indep, 
					recall_rate_eqtl, 
					recall_rate_ase,
					recall_rate_caviar,
					recall_rate_caviar_ase
				)
			)
		try:
			sns.set(style="white")
			sns.distplot(
				set_sizes_full,
				hist=False,
				kde=True,
				kde_kws={"linewidth": 3, "shade":True},
				label="Full"
			)
			sns.distplot(
				set_sizes_indep,
				hist=False,
				kde=True,
				kde_kws={"linewidth": 3, "shade":True},
				label="Independent Likelihoods"
			)
			sns.distplot(
				set_sizes_eqtl,
				hist=False,
				kde=True,
				kde_kws={"linewidth": 3, "shade":True},
				label="eQTL-Only"
			)
			sns.distplot(
				set_sizes_ase,
				hist=False,
				kde=True,
				kde_kws={"linewidth": 3, "shade":True},
				label="ASE-Only"
			)
			sns.distplot(
				set_sizes_caviar,
				hist=False,
				kde=True,
				kde_kws={"linewidth": 3, "shade":True},
				label="CAVIAR"
			)
			sns.distplot(
				set_sizes_caviar_ase,
				hist=False,
				kde=True,
				kde_kws={"linewidth": 3, "shade":True},
				label="CAVIAR-ASE"
			)
			plt.xlim(0, None)
			plt.legend(title="Model")
			plt.xlabel("Set Size")
			plt.ylabel("Density")
			plt.title("Distribution of Causal Set Sizes, {0} = {1}".format(title_var, var_value))
			plt.savefig(os.path.join(out_dir, "Set_size_distribution.svg"))
			plt.clf()		
		except Exception:
			pass

	def output_summary(self):
		recall_rate_full = [i["recall_rate_full"] for i in self.results]
		recall_rate_indep = [i["recall_rate_indep"] for i in self.results]
		recall_rate_eqtl = [i["recall_rate_eqtl"] for i in self.results]
		recall_rate_ase = [i["recall_rate_ase"] for i in self.results]
		recall_rate_caviar = [i["recall_rate_caviar"] for i in self.results]
		recall_rate_caviar_ase = [i["recall_rate_caviar_ase"] for i in self.results]
		# sets_full = [i["set_sizes_full"] for i in self.results]
		# sets_eqtl = [i["set_sizes_eqtl"] for i in self.results]

		title_var = self.params["primary_var_display"]
		num_trials = self.test_count

		rec_dict = {
			title_var: 4 * self.primary_var_vals,
			"Recall Rate": (
				recall_rate_full 
				+ recall_rate_indep 
				+ recall_rate_eqtl 
				+ recall_rate_ase
				+ recall_rate_caviar
				+ recall_rate_caviar_ase
			),
			"Model Type": (
				num_trials * ["Full"]
				+ num_trials * ["Independent Likelihoods"]
				+ num_trials * ["eQTL-Only"]
				+ num_trials * ["ASE-Only"]
				+ num_trials * ["CAVIAR"]
				+ num_trials * ["CAVIAR-ASE"]
			)
		}
		# print(rec_dict) ####
		rec_df = pd.DataFrame(rec_dict)

		sns.set(style="white")
		sns.lmplot(title_var, "Recall Rate", rec_df, hue="Model Type")
		# sns.lmplot(self.primary_var_vals, recall_full)
		# sns.lmplot(self.primary_var_vals, recall_indep)
		# sns.lmplot(self.primary_var_vals, recall_eqtl)
		# sns.lmplot(self.primary_var_vals, recall_ase)
		# plt.legend(title="Model")
		# plt.xlabel(title_var)
		# plt.ylabel("Recall Rate")
		plt.title("Recall Rates Across {0}".format(title_var))
		plt.savefig(os.path.join(self.output_path, "recalls.svg"))
		plt.clf()

		dflst = []
		for ind, dct in enumerate(self.results):
			var_value = self.primary_var_vals[ind]
			for i in dct["set_sizes_full"]:
				dflst.append([i, var_value, "Full"])
			for i in dct["set_sizes_eqtl"]:
				dflst.append([i, var_value, "eQTL-Only"])
		res_df = pd.DataFrame(dflst, columns=["Set Size", title_var, "Model"])
		
		sns.set(style="whitegrid")
		sns.violinplot(
			x=title_var,
			y="Set Size",
			hue="Model",
			data=res_df,
			split=True,
			inner="quartile"
		)
		plt.title("Causal Set Sizes across {0}".format(title_var))
		plt.savefig(os.path.join(self.output_path, "causal_sets.svg"))
		plt.clf()

	def set_output_folder(self):
		count_str = str(self.counter + 1).zfill(self.count_digits)
		test_folder = "{0}_{1}_{2}".format(
			count_str, 
			self.params["primary_var"], 
			str(self.params[self.params["primary_var"]])
		)
		test_path = os.path.join(self.output_path, test_folder)
		os.makedirs(test_path)
		self.counter += 1
		return test_path
	
	@staticmethod
	def _recall(causal_set, causal_config):
		recall = 1
		for ind, val in enumerate(causal_config):
			if val == 1:
				if causal_set[ind] != 1:
					recall = 0
		return recall


	def test(self, **kwargs):
		# count_str = str(self.counter + 1).zfill(self.count_digits)
		# test_folder = "{0}_{1}_{2}".format(
		# 	count_str, 
		# 	self.params["primary_var"], 
		# 	str(self.params[self.params["primary_var"]])
		# )
		# test_path = os.path.join(self.output_path, test_folder)
		# os.makedirs(test_path)

		for k, v in kwargs.viewitems():
			self.params[k] = v
		self.update_model_params()
		self.update_sim_params()

		result = {
			"set_sizes_full": [],
			"set_sizes_indep": [],
			"set_sizes_eqtl": [],
			"set_sizes_ase": [],
			"set_sizes_caviar": [],
			"set_sizes_caviar_ase": [],
			"recall_full": [],
			"recall_indep": [],
			"recall_eqtl": [],
			"recall_ase": [],
			"recall_caviar": [],
			"recall_caviar_ase": [],
		}
		
		num_ppl = self.params["num_ppl"]
		eqtl_herit = 1 - self.params["prop_noise_eqtl"]
		ase_herit = 1 - self.params["prop_noise_ase"]

		coverage = self.params["coverage"]
		overdispersion = self.params["overdispersion"]
		std_fraction = self.params["std_fraction"]
		ase_inherent_var = (np.log(std_fraction) - np.log(1-std_fraction))**2
		ase_count_var = (
			2 / coverage
			* (
				1 
				+ (
					1
					/ (
						1 / (np.exp(ase_inherent_var / 2))
						+ 1 / (np.exp(ase_inherent_var / 2)**3)
						* (
							(np.exp(ase_inherent_var * 2) + 1) / 2
							- np.exp(ase_inherent_var)
						)
					)
				)
			)
			* (1 + overdispersion * (coverage - 1))
		)
		correction = ase_inherent_var / (ase_inherent_var + ase_count_var)
		# print(correction) ####
		# ase_count_var_simple = ( ####
		# 	2 / coverage
		# 	* (
		# 		1 
		# 		+ (
		# 			1
		# 			/ (
		# 				1 / (np.exp(ase_inherent_var / 2))
		# 			)
		# 		)
		# 	)
		# 	* (1 + overdispersion * (coverage - 1))
		# )
		# print(ase_inherent_var / (ase_inherent_var + ase_count_var_simple)) ####
		# raise(Exception) ####
		ase_herit_adj = ase_herit * correction
		# ase_herit_adj = ase_herit ####

		corr_stats = np.sqrt(
			num_ppl**2 * eqtl_herit * ase_herit_adj
			/ (
				(1 + eqtl_herit * (num_ppl - 1))
				* (1 + ase_herit_adj * (num_ppl - 1))
			)
		)
		# print(corr_stats) ####
		iv = (
			(num_ppl * ase_herit_adj / (1 - ase_herit_adj)) 
		)
		xv = (
			(num_ppl * eqtl_herit / (1 - eqtl_herit)) 
		)
		unbias = lambda x: x * np.log(
			1
			+ x * (2 * x + 1) / (2 * (x + 1))
			+ x**2 * (3 * x + 1) / (3 * (x + 1)**2)
			+ x**3 * (2 * (2 * x + 1)**2 + 48 * (4 * x + 1)) / (192 * (x + 1)**3)
		)
		imbalance_var_prior = unbias(iv)
		total_exp_var_prior = unbias(xv)

		# print(np.sqrt(total_exp_var_prior)) ####
		# print(np.sqrt(imbalance_var_prior)) ####
		# raise ####
		
		# eqtl_cstats = [] ####

		for itr in xrange(self.params["iterations"]):
			print("\nIteration {0}".format(str(itr + 1)))
			# print("Generating Simulation Data")
			self.simulation.generate_data()
			sim_result = {
				"counts_A": self.simulation.counts_A,
				"counts_B": self.simulation.counts_B,
				"total_exp": self.simulation.total_exp,
				"hap_A": self.simulation.hap_A,
				"hap_B": self.simulation.hap_B
			}
			causal_config = self.simulation.causal_config
			# print(causal_config) ####
			# print("Finished Generating Simulation Data")

			# print(sim_result["hap_A"].tolist()) ####
			# print(sim_result["hap_B"].tolist()) ####
			# null = tuple([0] * self.params["num_snps"]) ####

			# print("Initializing Full Model")
			model_inputs = self.model_params.copy()
			model_inputs.update(sim_result)
			model_inputs.update({
				"corr_stats": corr_stats,
				"imbalance_var_prior": imbalance_var_prior,
				"total_exp_var_prior": total_exp_var_prior
			})
			# print(model_inputs) ####
			model_full = Finemap(**model_inputs)
			model_full.initialize()
			# print("Finished Initializing Full Model")
			# print("Starting Search")
			if self.params["search_mode"] == "exhaustive":
				model_full.search_exhaustive(self.params["min_causal"], self.params["max_causal"])
			elif self.params["search_mode"] == "shotgun":
				model_full.search_shotgun(self.params["search_iterations"])
			# print("Finished Search Under Full Model")

			causal_set = model_full.get_causal_set(self.params["confidence"])
			assert all([i == 0 or i == 1 for i in causal_set])
			causal_set_size = sum(causal_set)
			result["set_sizes_full"].append(causal_set_size)
			# print(causal_set_size) ####
			# print(model_full.get_probs()[tuple(causal_config)]) ####
			# print(model_full.get_probs()[null]) ####
			x = model_full.imbalance_stats
			result["max_stat_ase_full"] = abs(max(x.min(), x.max(), key=abs) )


			recall = self._recall(causal_set, causal_config)
			# for ind, val in enumerate(causal_config):
			# 	if val == 1:
			# 		if causal_set[ind] != 1:
			# 			recall = 0
			result["recall_full"].append(recall)
			# print(recall) ####
			# print(model_full.get_probs_sorted()[:10]) ####


			# print("Initializing Independent Model")
			model_inputs_indep = model_inputs.copy()
			model_inputs_indep.update({
				"cross_corr_prior": 0.0, 
				"corr_stats": 0.0,
				"imbalance_var_prior": imbalance_var_prior,
				"total_exp_var_prior": total_exp_var_prior
			})
			# print("Finished Initializing Independent Model")
			# print("Starting Search Under Independent Model")
			model_indep = Finemap(**model_inputs_indep)
			model_indep.initialize()
			if self.params["search_mode"] == "exhaustive":
				model_indep.search_exhaustive(self.params["min_causal"], self.params["max_causal"])
			elif self.params["search_mode"] == "shotgun":
				model_indep.search_shotgun(self.params["search_iterations"])
			# print("Finished Search Under Independent Model")

			causal_set_indep = model_indep.get_causal_set(self.params["confidence"])
			assert all([i == 0 or i == 1 for i in causal_set_indep])
			causal_set_indep_size = sum(causal_set_indep)
			result["set_sizes_indep"].append(causal_set_indep_size)
			# print(causal_set_indep_size) ####
			# print(model_eqtl.get_probs_sorted()) ####
			# model_eqtl.get_probs_sorted() ####
			# print(model_indep.get_probs()[tuple(causal_config)]) ####
			# print(model_indep.get_probs()[null]) ####
			x = model_indep.imbalance_stats
			result["max_stat_ase_indep"] = abs(max(x.min(), x.max(), key=abs)) 

			recall = self._recall(causal_set_indep, causal_config)
			# for ind, val in enumerate(causal_config):
			# 	if val == 1:
			# 		if causal_set_indep[ind] != 1:
			# 			recall = 0
			result["recall_indep"].append(recall)
			# print(recall) ####


			# print("Initializing eQTL Model")
			model_inputs_eqtl = model_inputs.copy()
			model_inputs_eqtl.update({
				"imbalance": np.zeros(shape=0), 
				"phases": np.zeros(shape=(0,0)),
				"imbalance_corr": np.zeros(shape=(0,0)),
				"imbalance_errors": np.zeros(shape=0),
				"imbalance_stats": np.zeros(shape=0),
				"num_ppl_imbalance": 0,
				"num_snps_imbalance": 0,
				"corr_stats": 0.0,
				"imbalance_var_prior": imbalance_var_prior,
				"total_exp_var_prior": total_exp_var_prior,
				"cross_corr_prior": 0.0,
			})
			# print("Finished Initializing eQTL Model")
			# print("Starting Search Under eQTL Model")
			model_eqtl = Finemap(**model_inputs_eqtl)
			model_eqtl.initialize()
			if self.params["search_mode"] == "exhaustive":
				model_eqtl.search_exhaustive(self.params["min_causal"], self.params["max_causal"])
			elif self.params["search_mode"] == "shotgun":
				model_eqtl.search_shotgun(self.params["search_iterations"])
			# print("Finished Search Under eQTL Model")

			causal_set_eqtl = model_eqtl.get_causal_set(self.params["confidence"])
			assert all([i == 0 or i == 1 for i in causal_set_eqtl])
			causal_set_eqtl_size = sum(causal_set_eqtl)
			result["set_sizes_eqtl"].append(causal_set_eqtl_size)
			# print(causal_set_eqtl_size) ####
			# print(model_eqtl.get_probs_sorted()) ####
			# model_eqtl.get_probs_sorted() ####
			# print(model_eqtl.get_probs()[tuple(causal_config)]) ####
			# print(model_eqtl.get_probs()[tuple(null)]) ####
			# ppas = model_eqtl.get_ppas()
			# np.savetxt("ppas_eqtl.txt", np.array(ppas)) ####
			# print(model_eqtl.total_exp_stats[causal_config == True][0]) ####
			# eqtl_cstats.append(model_eqtl.total_exp_stats[causal_config == True][0]) ####

			x = model_eqtl.imbalance_stats

			recall = self._recall(causal_set_eqtl, causal_config)
			# for ind, val in enumerate(causal_config):
			# 	if val == 1:
			# 		if causal_set_eqtl[ind] != 1:
			# 			recall = 0
			result["recall_eqtl"].append(recall)
			# print(recall) ####

			# print("Initializing ASE Model")
			model_inputs_ase = model_inputs.copy()
			model_inputs_ase.update({
				"total_exp": np.zeros(shape=0), 
				"genotypes_comb": np.zeros(shape=(0,0)),
				"total_exp_corr": np.zeros(shape=(0,0)),
				"total_exp_errors": np.zeros(shape=0),
				"total_exp_stats": np.zeros(shape=0),
				"num_ppl_total_exp": 0,
				"num_snps_total_exp": 0,
				"corr_stats": 0.0,
				"imbalance_var_prior": imbalance_var_prior,
				"total_exp_var_prior": total_exp_var_prior,
				"cross_corr_prior": 0.0,
			})
			# print("Finished Initializing ASE Model")
			# print("Starting Search Under ASE Model")
			model_ase = Finemap(**model_inputs_ase)
			model_ase.initialize()
			if self.params["search_mode"] == "exhaustive":
				model_ase.search_exhaustive(self.params["min_causal"], self.params["max_causal"])
			elif self.params["search_mode"] == "shotgun":
				model_ase.search_shotgun(self.params["search_iterations"])
			# print("Finished Search Under ASE Model")

			causal_set_ase = model_ase.get_causal_set(self.params["confidence"])
			assert all([i == 0 or i == 1 for i in causal_set_ase])
			causal_set_ase_size = sum(causal_set_ase)
			result["set_sizes_ase"].append(causal_set_ase_size)
			# print(causal_set_ase_size) ####
			# print(model_eqtl.get_probs_sorted()) ####
			# model_eqtl.get_probs_sorted() ####
			# print(model_ase.get_probs()[tuple(causal_config)]) ####
			# print(model_ase.get_probs()[tuple(null)]) ####
			x = model_ase.imbalance_stats
			result["max_stat_ase_ase"] = abs(max(x.min(), x.max(), key=abs)) 

			recall = self._recall(causal_set_ase, causal_config)
			# for ind, val in enumerate(causal_config):
			# 	if val == 1:
			# 		if causal_set_ase[ind] != 1:
			# 			recall = 0
			result["recall_ase"].append(recall)
			# print(recall) ####

			# if causal_set_ase_size == 181: ####
			# 	ps = model_ase.get_probs_sorted()
			# 	with open("null_ase.txt", "w") as null_ase:
			# 		null_ase.write("\n".join("\t".join(str(j) for j in i) for i in ps))
			# 	# np.savetxt("null_ase.txt", np.array(model_ase.get_probs_sorted()))
			# 	raise Exception

			model_caviar = EvalCaviar(
				model_full, 
				self.params["confidence"], 
				self.params["max_causal"]
			)
			model_caviar.run()
			causal_set_caviar = model_caviar.causal_set
			causal_set_caviar_size = sum(causal_set_caviar)
			result["set_sizes_caviar"].append(causal_set_caviar_size)
			recall = self._recall(causal_set_caviar, causal_config)
			result["recall_caviar"].append(recall)

			model_caviar_ase = EvalCaviarASE(
				model_full, 
				self.params["confidence"], 
				self.params["max_causal"]
			)
			model_caviar.run()
			causal_set_caviar_ase = model_caviar_ase.causal_set
			causal_set_caviar_size_ase = sum(causal_set_caviar_ase)
			result["set_sizes_caviar_ase"].append(causal_set_caviar_size_ase)
			recall = self._recall(causal_set_caviar_ase, causal_config)
			result["recall_caviar_ase"].append(recall)


		# print(np.std(eqtl_cstats)) ####
		
		print("Writing Result")
		self.primary_var_vals.append(self.params[self.params["primary_var"]])
		result["recall_rate_full"] = np.mean(result["recall_full"])
		result["recall_rate_indep"] = np.mean(result["recall_indep"])
		result["recall_rate_eqtl"] = np.mean(result["recall_eqtl"])
		result["recall_rate_ase"] = np.mean(result["recall_ase"])
		test_path = self.set_output_folder()
		self.output_result(result, test_path)
		self.results.append(result)
		print("Finished Writing Result")



class Benchmark2d(Benchmark):
	def __init__(self, params):
		self.secondary_var_vals = []
		super(Benchmark2d, self).__init__(params)

	def set_output_folder(self):
		count_str = str(self.counter + 1).zfill(self.count_digits)
		test_folder = "{0}_{1}_{2}_{3}_{4}".format(
			count_str, 
			self.params["primary_var"], 
			str(self.params[self.params["primary_var"]]),
			self.params["secondary_var"], 
			str(self.params[self.params["secondary_var"]])
		)
		test_path = os.path.join(self.output_path, test_folder)
		os.makedirs(test_path)
		self.counter += 1
		return test_path

	@staticmethod
	def plot_heatmap(
		primary, 
		pname, 
		secondary, 
		sname, 
		vals_full,
		vals_indep,
		vals_eqtl,
		vals_ase,
		vals_caviar,
		vals_caviar_ase,
		vname, 
		title_base, 
		output_path, 
		output_name_base
	):
		sns.set()

		if vals_full is not None:
			df_full = pd.DataFrame({
				sname: secondary,
				pname: primary,
				vname: vals_full,
			}).pivot(
				sname,
				pname,
				vname
			)

			title_full = title_base + " (Full Model)"
			output_name_full = output_name_base + "_full.svg"
			sns.heatmap(df_full, annot=True, linewidths=1.5)
			plt.title(title_full)
			plt.savefig(os.path.join(output_path, output_name_full))
			plt.clf()

		if vals_indep is not None:
			df_indep = pd.DataFrame({
				sname: secondary,
				pname: primary,
				vname: vals_indep,
			}).pivot(
				sname,
				pname,
				vname
			)

			title_indep = title_base + " (Independent Likelihoods)"
			output_name_indep = output_name_base + "_indep.svg"
			sns.heatmap(df_indep, annot=True, linewidths=1.5)
			plt.title(title_indep)
			plt.savefig(os.path.join(output_path, output_name_indep))
			plt.clf()

		if vals_eqtl is not None:
			df_eqtl = pd.DataFrame({
				sname: secondary,
				pname: primary,
				vname: vals_eqtl,
			}).pivot(
				sname,
				pname,
				vname
			)

			title_eqtl = title_base + " (eQTL-Only)"
			output_name_eqtl = output_name_base + "_eqtl.svg"
			sns.heatmap(df_eqtl, annot=True, linewidths=1.5)
			plt.title(title_eqtl)
			plt.savefig(os.path.join(output_path, output_name_eqtl))
			plt.clf()

		if vals_ase is not None:
			df_ase = pd.DataFrame({
				sname: secondary,
				pname: primary,
				vname: vals_ase,
			}).pivot(
				sname,
				pname,
				vname
			)

			title_ase = title_base + " (ASE-Only)"
			output_name_ase = output_name_base + "_ase.svg"
			sns.heatmap(df_ase, annot=True, linewidths=1.5)
			plt.title(title_ase)
			plt.savefig(os.path.join(output_path, output_name_ase))
			plt.clf()

		if vals_caviar is not None:
			df_caviar = pd.DataFrame({
				sname: secondary,
				pname: primary,
				vname: vals_caviar,
			}).pivot(
				sname,
				pname,
				vname
			)

			title_caviar = title_base + " (CAVIAR)"
			output_name_caviar = output_name_base + "_caviar.svg"
			sns.heatmap(df_caviar, annot=True, linewidths=1.5)
			plt.title(title_caviar)
			plt.savefig(os.path.join(output_path, output_name_caviar))
			plt.clf()

		if vals_caviar_ase is not None:
			df_caviar_ase = pd.DataFrame({
				sname: secondary,
				pname: primary,
				vname: vals_caviar_ase,
			}).pivot(
				sname,
				pname,
				vname
			)

			title_caviar_ase = title_base + " (CAVIAR-ASE)"
			output_name_caviar_ase = output_name_base + "_caviar_ase.svg"
			sns.heatmap(df_caviar_ase, annot=True, linewidths=1.5)
			plt.title(title_caviar_ase)
			plt.savefig(os.path.join(output_path, output_name_caviar_ase))
			plt.clf()
	
	
	def output_summary(self):
		num_trials = self.test_count
		num_trials_primary = self.params["test_count_primary"]
		num_trials_secondary = self.params["test_count_secondary"]
		results2d = [[None for _ in xrange(num_trials_primary)] for _ in xrange(num_trials_secondary)]
		for x in xrange(num_trials):
			row = x // num_trials_primary
			col = x % num_trials_secondary
			results2d[row][col] = self.results[x]

		means_full = [np.mean(i["set_sizes_full"]) for i in self.results]
		means_indep = [np.mean(i["set_sizes_indep"]) for i in self.results]
		means_eqtl = [np.mean(i["set_sizes_eqtl"]) for i in self.results]
		means_ase = [np.mean(i["set_sizes_ase"]) for i in self.results]
		means_caviar = [np.mean(i["set_sizes_caviar"]) for i in self.results]
		means_caviar_ase = [np.mean(i["set_sizes_caviar_ase"]) for i in self.results]

		recall_rate_full = [i["recall_rate_full"] for i in self.results]
		recall_rate_indep = [i["recall_rate_indep"] for i in self.results]
		recall_rate_eqtl = [i["recall_rate_eqtl"] for i in self.results]
		recall_rate_ase = [i["recall_rate_ase"] for i in self.results]
		recall_rate_caviar = [i["recall_rate_caviar"] for i in self.results]
		recall_rate_caviar_ase = [i["recall_rate_caviar_ase"] for i in self.results]

		max_stat_ase_full = [i["max_stat_ase_full"] for i in self.results]
		max_stat_ase_indep = [i["max_stat_ase_indep"] for i in self.results]
		max_stat_ase_ase = [i["max_stat_ase_ase"] for i in self.results]

		# secondary = self.secondary_var_vals * num_trials_primary
		# primary =[i for i in self.primary_var_vals for _ in xrange(num_trials_secondary)]

		secondary = self.secondary_var_vals
		primary = self.primary_var_vals

		# print(self.secondary_var_vals) ####
		# print(self.primary_var_vals)
		# print(secondary) ####
		# print(primary) ####
		# print(means_full) ####

		self.plot_heatmap(
			primary,
			self.params["primary_var_display"],
			secondary,
			self.params["secondary_var_display"],
			means_full,
			means_indep,
			means_eqtl,
			means_ase,
			means_caviar,
			means_caviar_ase,
			"Mean Causal Set Size",
			"Mean Causal Set Sizes",
			self.output_path,
			"causal_sets"
		)

		self.plot_heatmap(
			primary,
			self.params["primary_var_display"],
			secondary,
			self.params["secondary_var_display"],
			recall_rate_full,
			recall_rate_indep,
			recall_rate_eqtl,
			recall_rate_ase,
			recall_rate_caviar,
			recall_rate_ase,
			"Recall Rate",
			"Recall Rates",
			self.output_path,
			"recall"
		)

		self.plot_heatmap(
			primary,
			self.params["primary_var_display"],
			secondary,
			self.params["secondary_var_display"],
			max_stat_ase_full,
			max_stat_ase_indep,
			None,
			max_stat_ase_ase,
			None,
			None,
			"Max Association Stat",
			"Max Association Statistics",
			self.output_path,
			"max_stat_ase"
		)


		# df_full = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Mean Causal Set Size": means_full,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Mean Causal Set Size"
		# )
		# df_indep = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Mean Causal Set Size": means_indep,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Mean Causal Set Size"
		# )
		# df_eqtl = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Mean Causal Set Size": means_eqtl,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Mean Causal Set Size"
		# )
		# df_ase = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Mean Causal Set Size": means_ase,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Mean Causal Set Size"
		# )

		# df_full_recall = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Recall Rate": recall_rate_full,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Recall Rate"
		# )
		# df_indep_recall = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Recall Rate": recall_rate_indep,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Recall Rate"
		# )
		# df_eqtl_recall = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Recall Rate": recall_rate_eqtl,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Recall Rate"
		# )
		# df_ase_recall = pd.DataFrame({
		# 	self.params["secondary_var_display"]: secondary,
		# 	self.params["primary_var_display"]: primary,
		# 	"Recall Rate": recall_rate_ase,
		# }).pivot(
		# 	self.params["secondary_var_display"],
		# 	self.params["primary_var_display"],
		# 	"Recall Rate"
		# )

		# sns.set()

		# sns.heatmap(df_full, annot=True, linewidths=1)
		# plt.title("Mean Causal Set Sizes (Full Model)")
		# plt.savefig(os.path.join(self.output_path, "causal_sets_full.svg"))
		# plt.clf()

		# sns.heatmap(df_indep, annot=True, linewidths=1)
		# plt.title("Mean Causal Set Sizes (Independent Likelihoods)")
		# plt.savefig(os.path.join(self.output_path, "causal_sets_indep.svg"))
		# plt.clf()

		# sns.heatmap(df_eqtl, annot=True, linewidths=1)
		# plt.title("Mean Causal Set Sizes (eQTL-Only)")
		# plt.savefig(os.path.join(self.output_path, "causal_sets_eqtl.svg"))
		# plt.clf()

		# sns.heatmap(df_ase, annot=True, linewidths=1)
		# plt.title("Mean Causal Set Sizes (ASE-Only)")
		# plt.savefig(os.path.join(self.output_path, "causal_sets_ase.svg"))
		# plt.clf()

		# sns.heatmap(df_full_recall, annot=True, linewidths=1)
		# plt.title("Recall Rate (Full Model)")
		# plt.savefig(os.path.join(self.output_path, "recall_full.svg"))
		# plt.clf()

		# sns.heatmap(df_indep_recall, annot=True, linewidths=1)
		# plt.title("Recall Rate (Independent Likelihoods)")
		# plt.savefig(os.path.join(self.output_path, "recall_indep.svg"))
		# plt.clf()

		# sns.heatmap(df_eqtl_recall, annot=True, linewidths=1)
		# plt.title("Recall Rate (eQTL-Only)")
		# plt.savefig(os.path.join(self.output_path, "recall_eqtl.svg"))
		# plt.clf()

		# sns.heatmap(df_ase_recall, annot=True, linewidths=1)
		# plt.title("Recall Rate (ASE-Only)")
		# plt.savefig(os.path.join(self.output_path, "recall_ase.svg"))
		# plt.clf()

	def test(self, **kwargs):
		super(Benchmark2d, self).test(**kwargs)
		self.secondary_var_vals.append(self.params[self.params["secondary_var"]])