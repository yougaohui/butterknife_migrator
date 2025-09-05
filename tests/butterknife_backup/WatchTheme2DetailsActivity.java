package xfkj.fitpro.activity.clockDial.watchTheme2;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.blankj.utilcode.util.ImageUtils;
import com.blankj.utilcode.util.StringUtils;
import java.util.ArrayList;
import java.util.List;
import xfkj.fitpro.R;
import xfkj.fitpro.activity.clockDial.WatchThemeDetailsBaseActivity;
import xfkj.fitpro.activity.clockDial.WatchThemeHelper;
import xfkj.fitpro.base.adapter.BaseHolder;
import xfkj.fitpro.base.adapter.DefaultAdapter;
import xfkj.fitpro.model.sever.reponse.WatchThemeDetailsResponse;
import xfkj.fitpro.utils.PictureSelectorUtils;
import xfkj.fitpro.utils.glide.GlideUitls;
import xfkj.fitpro.view.ColorPannelView;
import xfkj.fitpro.view.SpaceItemDecoration;
public class WatchTheme2DetailsActivity extends WatchThemeDetailsBaseActivity {
    RecyclerView mColorList;
    ImageView mPreview1;
    ImageView mPreview2;
    RadioGroup mRadGroup;
    View mFrmPreview;
    RadioButton mRadPos1;
    RadioButton mRadPos2;
    RadioButton mRadPos3;
    RadioButton mRadPos4;
    @Override
    public int getLayoutId() {
        return R.layout.activity_watch_theme2_details;
    }
    @Override
    public void initData(Bundle savedInstanceState) {
        super.initData(savedInstanceState);
        LinearLayout.LayoutParams params = (LinearLayout.LayoutParams) mFrmPreview.getLayoutParams();
        params.height = (int) WatchThemeHelper.getConvertHeight(params.width);
        mFrmPreview.setLayoutParams(params);
        List colors = new ArrayList();
        for (int color : COLORS) {
            ColorModel colorModel = new ColorModel(color);
            colors.add(colorModel);
        }
        ColorAdapter adapter = new ColorAdapter(colors);
        mColorList.setAdapter(adapter);
        mColorList.setLayoutManager(new GridLayoutManager(mContext, 6));
        mColorList.addItemDecoration(new SpaceItemDecoration(0, 0, 0, 20));
        adapter.setOnItemClickListener((view, viewType, data, position) -> {
            mCurSelectedColor = (ColorModel) data;
            adapter.notifyDataSetChanged();
        });
        mCurBean = getRotationBeanByName(DERECTION_LABELS[0]);
        showImgPreView(null);
        changeDerectionPreview();
        if (mClockInfo.getScreenType() == 1) {
            mRadPos1.setText(R.string.pos_direction_1);
            mRadPos2.setText(R.string.pos_direction_2);
            mRadPos3.setText(R.string.pos_direction_3);
            mRadPos4.setText(R.string.pos_direction_4);
        }
    }
    @Override
    public void initListener() {
        super.initListener();
        mRadGroup.setOnCheckedChangeListener((radioGroup, i) -> {
            switch (i) {
                case R.id.rad_pos_left_top:
                    mCurBean = getRotationBeanByName(DERECTION_LABELS[0]);
                    break;
                case R.id.rad_pos_right_top:
                    mCurBean = getRotationBeanByName(DERECTION_LABELS[1]);
                    break;
                case R.id.rad_pos_right_bottom:
                    mCurBean = getRotationBeanByName(DERECTION_LABELS[2]);
                    break;
                case R.id.rad_pos_left_bottom:
                    mCurBean = getRotationBeanByName(DERECTION_LABELS[3]);
                    break;
            }
            changeDerectionPreview();
        });
        
        // 新增的点击事件监听器
        // 初始化点击事件 - 替换@OnClick注解
        findViewById(R.id.btn_choise_img).setOnClickListener(v -> mOnClickBtn(v));

        findViewById(R.id.btn_install).setOnClickListener(v -> mOnClickBtn(v));

        findViewById(R.id.btn_install).setOnClickListener(v -> onMBtnUpgradeClicked());

    }
    public class ColorAdapter extends DefaultAdapter<ColorModel> {
        public ColorAdapter(List infos) {
            super(infos);
        }
        @Override
        public BaseHolder getHolder(View v, int viewType) {
            return new ColorHolder(v);
        }
        @Override
        public int getLayoutId(int viewType) {
            return R.layout.item_layout_color_pannel;
        }
        public class ColorHolder extends BaseHolder<ColorModel> {
            View mImgSelected;
            ColorPannelView mColorPannelView;
            public ColorHolder(View itemView) {
                super(itemView);
        // 初始化View绑定 - 替换@BindView注解
        mImgSelected = itemView.findViewById(R.id.img_selected);
        mColorPannelView = itemView.findViewById(R.id.colorPannelView);

            }
            @Override
            public void setData(ColorModel data, int position) {
                if (mCurSelectedColor != null && mCurSelectedColor.getColor() == data.getColor()) {
                    mImgSelected.setVisibility(View.VISIBLE);
                } else {
                    mImgSelected.setVisibility(View.GONE);
                }
                mColorPannelView.setmColor(data.getColor());
            }
        }
    }
    public class ColorModel {
        int color;
        public ColorModel(int color) {
            this.color = color;
        }
        public int getColor() {
            return color;
        }
    }
    public void mOnClickBtn(View view) {
        switch (view.getId()) {
            case R.id.btn_choise_img:
                PictureSelectorUtils.startBiaoPanPictureSelector(this, mClockInfo.getWidth(), mClockInfo.getHeight());
                break;
            case R.id.btn_back:
                break;
        }
    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
    }
    /**
     * 预览图显示
     */
    protected void showImgPreView(View view) {
        String previewPath = mCurData.getPreviewImgPath();
        if (!StringUtils.isTrimEmpty(previewPath)) {
            GlideUitls.loadLocal(mContext, previewPath, mPreview1, mClockInfo.getScreenType() == 1);
        } else {
            GlideUitls.loadLocal(mContext, findBgImgUrlData().getUrl(), mPreview1, mClockInfo.getScreenType() == 1);
        }
    }
    @Override
    protected boolean isShowDialog() {
        return true;
    }
    @Override
    protected Bitmap getThumbSrcBitmap() {
        return ImageUtils.view2Bitmap(mFrmPreview);
    }
    /**
     * 替换方向图片
     */
    private void changeDerectionPreview() {
        GlideUitls.loadLocal(mContext, mCurBean.getUrl(), -1, mPreview2, null);
        convertDirection();
    }
    private WatchThemeDetailsResponse.MaterialListBean getRotationBeanByName(String derectionLabel) {
        List<WatchThemeDetailsResponse.MaterialListBean> items = mCurData.getMaterialList();
        for (WatchThemeDetailsResponse.MaterialListBean item : items) {
            if (StringUtils.equalsIgnoreCase(item.getName(), derectionLabel)) {
                return item;
            }
        }
        return items.get(0);
    }
    public void onMBtnUpgradeClicked() {
        handleClickInstallWatchTheme();
    }

    @Override
    protected void initViews() {
        super.initViews();
        // 初始化View绑定 - 替换@BindView注解
        mColorList = findViewById(R.id.color_list);
        mPreview1 = findViewById(R.id.preview1);
        mPreview2 = findViewById(R.id.preview2);
        mRadGroup = findViewById(R.id.radGroup);
        mRadPos1 = findViewById(R.id.rad_pos_left_top);
        mRadPos2 = findViewById(R.id.rad_pos_right_top);
        mRadPos3 = findViewById(R.id.rad_pos_left_bottom);
        mRadPos4 = findViewById(R.id.rad_pos_right_bottom);
    }
}