import numpy as np

import brainlit
from brainlit.utils.ngl_pipeline import NeuroglancerSession
from brainlit.viz.swc import *
from brainlit.viz import visualize
import matplotlib
import SimpleITK as sitk
import napari


ngl_sess = NeuroglancerSession(mip=1)
img, bbbox, vox = ngl_sess.pull_chunk(2, 300, 1, 1, 1)
img_slices = [img[:, 100, :], img[:, 99, :], img[:, 97, :], img[:, 96, :]]
img_list = [img, img]


def test_fig_plot_3d():
    """test if fig output is correct type (matplotlib figure)"""
    url = "s3://mouse-light-viz/precomputed_volumes/brain1"
    seg_id = 11
    mip = 2
    df = read_s3(url + "_segments", seg_id, mip)

    df["sample"].size  # the number of vertex IDs [1, 2, ..., df['sample'].size]
    subneuron_df = df[0:5]  # choose vertices to use for the subneuron
    vertex_list = subneuron_df["sample"].array
    ngl = NeuroglancerSession(url, mip=mip)
    buffer = [10, 10, 10]
    img, bounds, vox_in_img_list = ngl.pull_vertex_list(
        seg_id, vertex_list, buffer=buffer, expand=True
    )

    napari.gui_qt()

    fig_2d, axis_2d = visualize.plot_3d(
        sitk.GetImageFromArray(np.squeeze(img), isVector=False),
        zslices=range(48, 53),
        title="Downloaded Mouselight Volume",
        show_plot=False,
    )
    assert isinstance(fig_2d, matplotlib.figure.Figure)
    assert isinstance(axis_2d, matplotlib.axes._subplots.Subplot)


def test_fig_plot_image_2d_given_one():
    """test if fig output is correct type (matplotlib figure)"""
    fig_2d, axis_2d = visualize.plot_image_2d(
        img[:, 100, :], titles=["test"], colorbar=True
    )
    assert isinstance(fig_2d, matplotlib.figure.Figure)
    assert isinstance(axis_2d, matplotlib.axes._subplots.Subplot)


def test_fig_plot_image_2d_given_list():
    """test if fig output is correct type (matplotlib figure)"""
    fig_2d_list, ax_2d_list = visualize.plot_image_2d(img_slices)
    assert isinstance(fig_2d_list, matplotlib.figure.Figure)
    for ax in ax_2d_list:
        assert isinstance(ax, matplotlib.axes._subplots.Subplot)


def test_fig_plot_mip_given_one():
    """test if output is correct type (matplotlib figure)"""
    fig_3d, ax_3d = visualize.plot_image_mip(img)
    assert isinstance(fig_3d, matplotlib.figure.Figure)
    assert isinstance(ax_3d, matplotlib.axes._subplots.Subplot)


def test_fig_plot_mip_given_list():
    """test if output is correct type (matplotlib figure)"""
    fig_3d_list, ax_3d_list = visualize.plot_image_mip(img_list)
    assert isinstance(fig_3d_list, matplotlib.figure.Figure)
    for ax in ax_3d_list:
        assert isinstance(ax, matplotlib.axes._subplots.Subplot)


def test_find_smalldim():
    """test if output is correct type (int)"""
    smallest_axis = visualize.find_smalldim(img)
    assert isinstance(smallest_axis, int)


def test_find_smalldim_list():
    """test if output is correct type (int)"""
    smallest_axis = visualize.find_smalldim(img_list)
    assert isinstance(smallest_axis, int)


def test_plot_image_hist():
    """test if output is correct type (tuple (n, bins, patches))"""
    hist_tuple = visualize.plot_image_hist(img)
    assert isinstance(hist_tuple, tuple)


def test_plot_image_hist_list():
    """test if output is correct type (tuple (n, bins, patches))"""
    hist_tuple = visualize.plot_image_hist(img_list)
    assert isinstance(hist_tuple, tuple)


def test_plot_img_pts():
    """test plot_image_pts method with voxels"""
    fig, axes = visualize.plot_image_pts(img[:, :, 100], vox, colorbar=True)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert isinstance(axes, matplotlib.axes._subplots.Subplot)
