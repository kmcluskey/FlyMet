const path = require("path");
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const IgnorePlugin =  require("webpack").IgnorePlugin;
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    context: __dirname,
    // As a rule of thumb: for each HTML document use exactly one entry point.
    entry: {
        base: './static/js/base',
        init_datatables: './static/js/init_datatables',
        metabolite_list: './static/js/metabolite_list',
        metabolite_search_tissue: './static/js/metabolite_search_tissue',
        metabolite_search_age: './static/js/metabolite_search_age',
        met_ex_all:'./static/js/met_ex_all',
        met_age_id: './static/js/met_age_id',
        met_age_all: './static/js/met_age_all',
        enzyme_search: './static/js/enzyme_search',
        pathway_search: './static/js/pathway_search',
        pathway_metabolites: './static/js/pathway_metabolites',
        gene_tissue_explorer: './static/js/gene_tissue_explorer',
        peak_explorer: './static/js/peak_explorer',
        peak_ex_compare: './static/js/peak_ex_compare',
        peak_mf_compare: './static/js/peak_mf_compare',
        pathway_explorer: './static/js/pathway_explorer',
        peak_age_explorer: './static/js/peak_age_explorer',
        peak_age_compare: './static/js/peak_age_compare',
        peak_mf_age_compare: './static/js/peak_mf_age_compare',
        pathway_age_explorer:'./static/js/pathway_age_explorer',
        pathway_age_search: './static/js/pathway_age_search',
        pathway_age_metabolites: './static/js/pathway_age_metabolites',
        gene_age_explorer: './static/js/gene_age_explorer',
        index_age:'./static/js/index_age',
        index:'./static/js/index',      
    },

    output: {
        filename: "[name]-[hash].js",
        path: path.resolve('./static/bundles/'),
    },

    optimization: {
    minimize: false
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new CleanWebpackPlugin(path.resolve('./static/bundles/')),
        new MiniCssExtractPlugin({
            filename: "[name]-[hash].css",
            chunkFilename: "[id]-[chunkhash].css"
        }),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            'window.jQuery': 'jquery',
            'window.$': 'jquery'
        }),
        // for alasql
        new IgnorePlugin(/(^fs$|cptable|jszip|xlsx|^es6-promise$|^net$|^tls$|^forever-agent$|^tough-cookie$|cpexcel|^path$|^request$|react-native|^vertx$)/),
    ],

    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader'
            },
            {
                test: /\.s?[ac]ss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    { loader: 'css-loader', options: { url: false, sourceMap: true } },
                    { loader: 'sass-loader', options: { sourceMap: true } }
                ],
            },
            {
                test: /\.(svg|gif|png|eot|woff|ttf)$/,
                loader: 'url-loader'
            },
            {
                // for django-select2
                // https://stackoverflow.com/questions/47469228/jquery-is-not-defined-using-webpack
                test: require.resolve('jquery'),
                use: [{
                    loader: 'expose-loader',
                    options: 'jQuery'
                },{
                    loader: 'expose-loader',
                    options: '$'
                }]
            }
        ],
    },

   devtool: 'source-map',

    resolve: {
        modules: ['node_modules', 'bower_components'],
        extensions: ['*', '.js', '.jsx'],
    },
}
