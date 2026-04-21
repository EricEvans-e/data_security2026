#pragma once

#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <libsnark/common/default_types/r1cs_gg_ppzksnark_pp.hpp>
#include <libsnark/gadgetlib1/pb_variable.hpp>
#include <libsnark/zk_proof_systems/ppzksnark/r1cs_gg_ppzksnark/r1cs_gg_ppzksnark.hpp>

namespace lab2 {

using ppT = libsnark::default_r1cs_gg_ppzksnark_pp;
using FieldT = libff::Fr<ppT>;

struct WitnessValues {
    long long x;
    long long x_square;
    long long x_cube;
    long long sum_with_x;
    long long expr_out;
};

inline void init_curve_once()
{
    static bool initialized = false;
    if (!initialized) {
        ppT::init_public_params();
        initialized = true;
    }
}

inline std::string artifact_path(const std::string &artifacts_dir, const std::string &filename)
{
    if (artifacts_dir.empty()) {
        return filename;
    }
    if (artifacts_dir.back() == '/' || artifacts_dir.back() == '\\') {
        return artifacts_dir + filename;
    }
    return artifacts_dir + "/" + filename;
}

inline long long parse_long_flag(const int argc, char *argv[], const std::string &flag, const long long default_value)
{
    for (int i = 1; i + 1 < argc; ++i) {
        if (flag == argv[i]) {
            std::stringstream ss(argv[i + 1]);
            long long value = default_value;
            ss >> value;
            if (ss.fail() || !ss.eof()) {
                throw std::runtime_error("invalid numeric value for " + flag);
            }
            return value;
        }
    }
    return default_value;
}

inline std::string parse_string_flag(const int argc, char *argv[], const std::string &flag, const std::string &default_value)
{
    for (int i = 1; i + 1 < argc; ++i) {
        if (flag == argv[i]) {
            return argv[i + 1];
        }
    }
    return default_value;
}

inline WitnessValues build_witness(const long long x)
{
    WitnessValues witness{};
    witness.x = x;
    witness.x_square = x * x;
    witness.x_cube = witness.x_square * x;
    witness.sum_with_x = witness.x_cube + x;
    witness.expr_out = witness.sum_with_x + 5;
    return witness;
}

inline bool witness_matches_statement(const WitnessValues &witness, const long long public_out)
{
    return witness.expr_out == public_out;
}

template<typename Field>
inline libsnark::protoboard<Field> build_protoboard(const long long public_out, const WitnessValues *witness = nullptr)
{
    init_curve_once();

    libsnark::protoboard<Field> pb;

    libsnark::pb_variable<Field> out;
    libsnark::pb_variable<Field> x;
    libsnark::pb_variable<Field> x_square;
    libsnark::pb_variable<Field> x_cube;
    libsnark::pb_variable<Field> sum_with_x;
    libsnark::pb_variable<Field> expr_out;

    out.allocate(pb, "out");
    x.allocate(pb, "x");
    x_square.allocate(pb, "x_square");
    x_cube.allocate(pb, "x_cube");
    sum_with_x.allocate(pb, "sum_with_x");
    expr_out.allocate(pb, "expr_out");

    pb.set_input_sizes(1);
    pb.val(out) = Field(public_out);

    pb.add_r1cs_constraint(libsnark::r1cs_constraint<Field>(x, x, x_square));
    pb.add_r1cs_constraint(libsnark::r1cs_constraint<Field>(x_square, x, x_cube));
    pb.add_r1cs_constraint(libsnark::r1cs_constraint<Field>(x_cube + x, 1, sum_with_x));
    pb.add_r1cs_constraint(libsnark::r1cs_constraint<Field>(sum_with_x + 5, 1, expr_out));
    pb.add_r1cs_constraint(libsnark::r1cs_constraint<Field>(expr_out, 1, out));

    if (witness != nullptr) {
        pb.val(x) = Field(witness->x);
        pb.val(x_square) = Field(witness->x_square);
        pb.val(x_cube) = Field(witness->x_cube);
        pb.val(sum_with_x) = Field(witness->sum_with_x);
        pb.val(expr_out) = Field(witness->expr_out);
    }

    return pb;
}

template<typename T>
inline void save_object(const std::string &path, const T &value)
{
    std::ofstream out(path.c_str(), std::ios_base::out | std::ios_base::trunc);
    if (!out) {
        throw std::runtime_error("failed to open output file: " + path);
    }
    out << value;
    out.close();
}

template<typename T>
inline T load_object(const std::string &path)
{
    std::ifstream in(path.c_str(), std::ios_base::in);
    if (!in) {
        throw std::runtime_error("failed to open input file: " + path);
    }
    T value;
    in >> value;
    in.close();
    return value;
}

inline void print_statement_banner(const std::string &title, const long long out_value)
{
    std::cout << "=== " << title << " ===" << std::endl;
    std::cout << "Public statement: x^3 + x + 5 = Out" << std::endl;
    std::cout << "Out = " << out_value << std::endl;
}

inline void print_witness_banner(const WitnessValues &witness)
{
    std::cout << "Witness x = " << witness.x << std::endl;
    std::cout << "x_square = " << witness.x_square << std::endl;
    std::cout << "x_cube = " << witness.x_cube << std::endl;
    std::cout << "sum_with_x = " << witness.sum_with_x << std::endl;
    std::cout << "expr_out = " << witness.expr_out << std::endl;
}

} // namespace lab2
